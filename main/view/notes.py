from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.db.models import F
from django.http import HttpResponseForbidden

from main.models import Notice, AccessRequest
import main.forms as forms

# 🔒 NOTICE LIST (faqat owner va public)
@login_required(login_url='/login/')
def notice_list_view(request):
    query = request.GET.get('q')
    object_list = Notice.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    )

    if query:
        filters = Q(title__icontains=query) | Q(main_text__icontains=query)
        if query.isdigit():
            filters |= Q(id=int(query))
        object_list = object_list.filter(filters)

    context = {
        "object_list": object_list.order_by('-created_at'),
        "query": query,
        "searched": bool(query),
    }
    return render(request, "notice/list.html", context)


# 🔒 CREATE NOTICE
@login_required(login_url='/login/')
def notice_create_view(request):
    if request.method == "POST":
        form = forms.NoticeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect("notice_list")
    else:
        form = forms.NoticeForm()

    return render(request, "notice/form.html", {"form": form})

@login_required(login_url="/login/")
def notice_detail_view(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)

    # 🔒 Faqat egasi ko‘ra oladi
    if notice.owner != request.user:
        return HttpResponseForbidden("Sizga bu sahifani ko‘rishga ruxsat yo‘q.")

    # 👁 VIEW +1 (har kirishda, owner bo‘lsa ham)
    Notice.objects.filter(id=notice.id).update(
        views=F("views") + 1
    )

    # 🔄 Yangilangan qiymatni olish
    notice.refresh_from_db()

    return render(request, "notice/detail.html", {"notice": notice})


# ✏️ EDIT (faqat owner)
@login_required(login_url='/login/')
def notice_edit_view(request, notice_id):
    notice = get_object_or_404(
        Notice,
        id=notice_id,
        owner=request.user
    )

    if request.method == "POST":
        form = forms.NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            return redirect("notice_detail", notice_id=notice.id)
    else:
        form = forms.NoticeForm(instance=notice)

    return render(request, "notice/form.html", {
        "form": form,
        "notice": notice
    })

def notice_public_view(request, public_id):
    notice = get_object_or_404(Notice, public_id=public_id)

    # 🔒 Private → login shart
    if not notice.is_public and not request.user.is_authenticated:
        return redirect(f'/login/?next=/notice/public/{notice.public_id}/')

    # ⏰ Expired
    if notice.expire_date and timezone.now() > notice.expire_date:
        return render(request, "notice/expired.html", {"notice": notice})

    # 🚫 Inactive
    if not notice.is_active:
        return render(request, "notice/inactive.html", {"notice": notice})

    # 👁 View count
    if notice.is_public:
        Notice.objects.filter(id=notice.id).update(public_views=F("public_views") + 1)
        notice.refresh_from_db()
        # PUBLIC TEMPLATE
        return render(request, "notice/public_detail.html", {"notice": notice})
    else:
        Notice.objects.filter(id=notice.id).update(views=F("views") + 1)
        notice.refresh_from_db()
        # PRIVATE TEMPLATE
        return render(request, "notice/detail.html", {"notice": notice})


# 🗑 DELETE (faqat owner)
@login_required(login_url='/login/')
def notice_delete_view(request, notice_id):
    notice = get_object_or_404(
        Notice,
        id=notice_id,
        owner=request.user
    )

    if request.method == "POST":
        notice.delete()
        return redirect("notice_list")

    return render(request, "notice/delete_confirm.html", {"notice": notice})

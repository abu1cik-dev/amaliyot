from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from django.utils import timezone
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseForbidden
from main.forms import UploadedFileForm
from main.models import UploadedFile, FileViewLog, FileDownloadLog

# -------------------------------
# OWNER FILE DETAIL (faqat o'z fayllari)
# -------------------------------
@login_required(login_url='/login/')
def file_detail_view(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)

    if file.owner != request.user:
        return HttpResponseForbidden("Sizga bu faylni ko‘rishga ruxsat yo‘q.")

    # Owner uchun ham view log
    FileViewLog.objects.create(file=file, user=request.user)
    UploadedFile.objects.filter(id=file.id).update(views_count=F('views_count') + 1)
    file.refresh_from_db()

    return render(request, "file/detail.html", {"file": file})


# -------------------------------
# LINK ORQALI FILE VIEW (public/private)
# -------------------------------
def file_public_view(request, public_id):
    file = get_object_or_404(UploadedFile, public_id=public_id)

    # 🔒 Private → faqat login shart
    if not file.is_public and not request.user.is_authenticated:
        return redirect(f'/login/?next=/file/public/{file.public_id}/')

    # ⏰ Expire
    if file.expire_date and timezone.now() > file.expire_date:
        return render(request, "file/expired.html", {"file": file})

    # 👁 View count
    UploadedFile.objects.filter(id=file.id).update(
        views_count=F('views_count') + 1
    )

    FileViewLog.objects.create(
        file=file,
        user=request.user if request.user.is_authenticated else None
    )

    return render(request, "file/detail.html", {"file": file})



# -------------------------------
# FILE LIST (faqat owner fayllari)
# -------------------------------
@login_required(login_url='/login/')
def file_list_view(request):
    query = request.GET.get('q')
    files = UploadedFile.objects.filter(owner=request.user).order_by('-created_at')

    if query:
        filters = Q(title__icontains=query)
        if query.isdigit():
            filters |= Q(id=int(query))
        files = files.filter(filters)

    return render(request, "file/list.html", {
        "object_list": files,
        "query": query or '',
    })


# -------------------------------
# FILE CREATE
# -------------------------------
@login_required(login_url='/login/')
def file_create_view(request):
    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            messages.success(request, "✅ Fayl muvaffaqiyatli yuklandi!")
            return redirect("file_list")
        else:
            messages.error(request, "❌ Iltimos, barcha maydonlarni to‘ldiring va fayl tanlang.")
    else:
        form = UploadedFileForm()
    
    return render(request, "file/form.html", {"form": form})


# -------------------------------
# FILE EDIT
# -------------------------------
@login_required(login_url='/login/')
def file_edit_view(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)

    if file.owner != request.user:
        messages.error(request, "⚠ Siz bu faylni tahrirlash huquqiga ega emassiz")
        return redirect('file_list')

    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            updated_file = form.save(commit=False)
            updated_file.owner = file.owner
            if updated_file.views_count is None:
                updated_file.views_count = 0
            if updated_file.downloaded_count is None:
                updated_file.downloaded_count = 0
            updated_file.save()
            messages.success(request, "✏️ Fayl muvaffaqiyatli yangilandi!")
            return redirect(file_list_view)
        else:
            print(form.errors)
    else:
        form = UploadedFileForm(instance=file)

    return render(request, "file/form.html", {"form": form, "file": file})


# -------------------------------
# FILE DELETE
# -------------------------------
@login_required(login_url='/login/')
def file_delete_view(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id, owner=request.user)

    if request.method == "POST":
        file.delete()
        messages.success(request, "🗑 Fayl muvaffaqiyatli o‘chirildi!")
        return redirect("file_list")

    return render(request, "file/delete_confirm.html", {"file": file})


# -------------------------------
# FILE DOWNLOAD
# -------------------------------
def file_download_view(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)

    # 🔒 PRIVATE → login shart
    if not file.is_public and not request.user.is_authenticated:
        return redirect(f'/login/?next=/file/{file.id}/')

    # ⏰ Expire
    if file.expire_date and timezone.now() > file.expire_date:
        raise Http404("Fayl muddati tugagan")

    # 📉 Download limit
    if file.download_limit is not None:
        if file.downloaded_count >= file.download_limit:
            raise Http404("Yuklab olish limiti tugagan")

    # 📈 Download count
    UploadedFile.objects.filter(id=file.id).update(
        downloaded_count=F('downloaded_count') + 1
    )

    FileDownloadLog.objects.create(
        file=file,
        user=request.user if request.user.is_authenticated else None
    )

    return FileResponse(
        file.file.open('rb'),
        as_attachment=True,
        filename=file.file.name
    )

def public_file_download_view(request, public_id):
    file = get_object_or_404(UploadedFile, public_id=public_id)

    # private bo‘lsa → login shart
    if not file.is_public and not request.user.is_authenticated:
        return redirect(f'/login/?next=/file/public/{file.public_id}/')

    if file.expire_date and timezone.now() > file.expire_date:
        raise Http404("Fayl muddati tugagan")

    if file.download_limit is not None:
        if file.downloaded_count >= file.download_limit:
            raise Http404("Yuklab olish limiti tugagan")

    UploadedFile.objects.filter(id=file.id).update(
        downloaded_count=F('downloaded_count') + 1
    )

    FileDownloadLog.objects.create(
        file=file,
        user=request.user if request.user.is_authenticated else None
    )

    return FileResponse(
        file.file.open('rb'),
        as_attachment=True,
        filename=file.file.name
    )

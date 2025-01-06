from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import *
from .forms import *
import pdfplumber
import os
import re
# Create your views here.


def pdf_file_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        form = PdfFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            if PdfFiles.objects.filter(file=uploaded_file.name).exists():
                messages.warning(
                    request, f"The file {uploaded_file.name} has already been processed.")
            else:
                form.save()
                messages.success(
                    request, f"File {uploaded_file.name} uploaded successfully!")
                return redirect('pdf-list')
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = PdfFileForm()

    return render(request, 'pdfs/upload.html', {'form': form})


def pdf_files_list(request):
    pdfs = PdfFiles.objects.all()
    return render(request, 'pdfs/pdfs_list.html', {'pdfs': pdfs})


def pdf_file_delete(request, pk):
    pdf = get_object_or_404(PdfFiles, pk=pk)

    if pdf.file:
        pdf.file.delete()
    pdf.delete()

    return redirect('pdf-list')


def extract_datas(request):

    Employee.objects.all().delete()

    # Set up FileSystemStorage with the location of the 'pdffiles' folder
    fs = FileSystemStorage(location=os.path.join(
        settings.MEDIA_ROOT, 'pdffiles'))

    # Get the list of all PDF files in the 'pdffiles' directory
    pdf_files = [file for file in fs.listdir('')[1] if file.endswith(
        '.pdf')]  # fs.listdir('') gets all files

    if request.method == 'GET':
        for pdf in pdf_files:
            pdf_path = fs.path(pdf)
            try:
                with pdfplumber.open(pdf_path) as pdf_file:
                    page = pdf_file.pages[0]
                    text = page.extract_text()

                # Define regular expressions for extracting name, designation, and salary
                name_pattern = r"Name:\s*(\w+\s\w+)"  # e.g., "Name: John Doe"
                designation_pattern = r"Designation:\s*(\w+\s\w+)"
                salary_pattern = r"(Salary)\s?\$?(\d{1,5}(?:,\d{3})*(?:\.\d{2})?)"

                # Extract information using regular expressions
                name_match = re.search(name_pattern, text)
                designation_match = re.search(designation_pattern, text)
                salary_match = re.search(salary_pattern, text)

                # Extract matched data, or set it to None if not found
                name = name_match.group(1) if name_match else None
                designation = designation_match.group(
                    1) if designation_match else None
                salary = salary_match.group(2) if salary_match else None

                if name and salary:
                    salary = float(salary.replace(',', '').replace(
                        '$', '').strip())  # Clean salary value
                    Employee.objects.create(
                        name=name,
                        designation=designation,
                        salary=salary
                    )
                else:
                    messages.error(request, f"Data not found in {pdf}.")
                    return redirect('pdf-list')

            except Exception as e:
                messages.error(request, f"Error processing {pdf}: {str(e)}")
                return redirect('pdf-list')

    employees = Employee.objects.all()

    return render(request, 'pdfs/employee_details.html', {'employees': employees})


def delete_all_data_and_files(request):
    if request.method == 'GET':
        for model in [PdfFiles, Employee]:
            model.objects.all().delete()

        # Step 2: Delete All Files in the Media Folder
        media_root = settings.MEDIA_ROOT
        for dirpath, dirnames, filenames in os.walk(media_root, topdown=False):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                os.remove(file_path)  # Remove individual files
            for dirname in dirnames:
                dir_path = os.path.join(dirpath, dirname)
                os.rmdir(dir_path)  # Remove empty directories

        return redirect('upload-pdf')

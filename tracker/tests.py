import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.test import APIClient

from .models import JobApplication, Attachment


class HireTrackFileAPITests(TestCase):

    def setUp(self):
        self.media_temp_dir = tempfile.TemporaryDirectory()
        self.media_override = override_settings(
            MEDIA_ROOT=self.media_temp_dir.name
        )
        self.media_override.enable()

        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123"
        )

        self.application = JobApplication.objects.create(
            user=self.user,
            candidate_name="Test Candidate",
            company="Test Company",
            role="Developer",
            legacy_id="test-application-1"
        )

        self.other_application = JobApplication.objects.create(
            user=self.other_user,
            candidate_name="Other Candidate",
            company="Other Company",
            role="Designer",
            legacy_id="test-application-2"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.media_override.disable()
        self.media_temp_dir.cleanup()
        super().tearDown()

    def test_user_can_only_see_own_applications(self):
        response = self.client.get(
            reverse("application-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["company"],
            "Test Company"
        )

    def test_user_can_upload_resume_and_cover_letter(self):
        resume = SimpleUploadedFile(
            "resume.pdf",
            b"Test resume content",
            content_type="application/pdf"
        )

        cover_letter = SimpleUploadedFile(
            "cover-letter.pdf",
            b"Test cover letter content",
            content_type="application/pdf"
        )

        response = self.client.patch(
            reverse(
                "application-detail",
                args=[self.application.id]
            ),
            {
                "resume_file": resume,
                "cover_letter_file": cover_letter,
            },
            format="multipart"
        )

        self.assertEqual(response.status_code, 200)

        self.application.refresh_from_db()

        self.assertTrue(self.application.resume_file)
        self.assertTrue(self.application.cover_letter_file)
        self.assertTrue(
            Path(self.application.resume_file.path).exists()
        )
        self.assertTrue(
            Path(self.application.cover_letter_file.path).exists()
        )

    def test_user_can_upload_attachment(self):
        uploaded_file = SimpleUploadedFile(
            "certificate.pdf",
            b"Test certificate content",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("attachment-list"),
            {
                "application": self.application.id,
                "file": uploaded_file,
                "original_name": "certificate.pdf",
            },
            format="multipart"
        )

        self.assertEqual(response.status_code, 201)

        attachment = Attachment.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            attachment.application_id,
            self.application.id
        )
        self.assertTrue(Path(attachment.file.path).exists())
        self.assertEqual(attachment.file_size, 24)

    def test_user_cannot_upload_to_another_users_application(self):
        uploaded_file = SimpleUploadedFile(
            "private.pdf",
            b"Private file",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("attachment-list"),
            {
                "application": self.other_application.id,
                "file": uploaded_file,
                "original_name": "private.pdf",
            },
            format="multipart"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Attachment.objects.count(), 0)

    def test_deleting_attachment_removes_physical_file(self):
        attachment = Attachment.objects.create(
            application=self.application,
            file=SimpleUploadedFile(
                "delete-test.pdf",
                b"Delete test content",
                content_type="application/pdf"
            ),
            original_name="delete-test.pdf",
            file_size=19
        )

        file_path = Path(attachment.file.path)
        self.assertTrue(file_path.exists())

        response = self.client.delete(
            reverse("attachment-detail", args=[attachment.id])
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Attachment.objects.filter(id=attachment.id).exists()
        )
        self.assertFalse(file_path.exists())


class ApplicationFileCleanupAPITests(TestCase):

    def setUp(self):
        self.media_temp_dir = tempfile.TemporaryDirectory()
        self.media_override = override_settings(
            MEDIA_ROOT=self.media_temp_dir.name
        )
        self.media_override.enable()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="cleanupuser",
            password="testpass123"
        )

        self.application = JobApplication.objects.create(
            user=self.user,
            candidate_name="Cleanup Candidate",
            company="Cleanup Company",
            role="Developer",
            resume_file=SimpleUploadedFile(
                "resume.pdf",
                b"Resume test content",
                content_type="application/pdf"
            ),
            cover_letter_file=SimpleUploadedFile(
                "cover-letter.pdf",
                b"Cover letter test content",
                content_type="application/pdf"
            )
        )

        self.attachment = Attachment.objects.create(
            application=self.application,
            file=SimpleUploadedFile(
                "certificate.pdf",
                b"Certificate test content",
                content_type="application/pdf"
            ),
            original_name="certificate.pdf"
        )

        self.file_paths = [
            Path(self.application.resume_file.path),
            Path(self.application.cover_letter_file.path),
            Path(self.attachment.file.path),
        ]

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.media_override.disable()
        self.media_temp_dir.cleanup()
        super().tearDown()

    def test_deleting_application_removes_all_physical_files(self):
        for file_path in self.file_paths:
            self.assertTrue(file_path.exists())

        response = self.client.delete(
            reverse("application-detail", args=[self.application.id])
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            JobApplication.objects.filter(
                id=self.application.id
            ).exists()
        )

        for file_path in self.file_paths:
            self.assertFalse(file_path.exists())

        self.assertFalse(
            Attachment.objects.filter(
                id=self.attachment.id
            ).exists()
        )

class ApplicationFileReplacementAPITests(TestCase):

    def setUp(self):
        self.media_temp_dir = tempfile.TemporaryDirectory()
        self.media_override = override_settings(
            MEDIA_ROOT=self.media_temp_dir.name
        )
        self.media_override.enable()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="replaceuser",
            password="testpass123"
        )

        self.application = JobApplication.objects.create(
            user=self.user,
            candidate_name="Replace Candidate",
            company="Replace Company",
            role="Developer",
            resume_file=SimpleUploadedFile(
                "old-resume.pdf",
                b"Old resume content",
                content_type="application/pdf"
            ),
            cover_letter_file=SimpleUploadedFile(
                "existing-cover.pdf",
                b"Existing cover content",
                content_type="application/pdf"
            )
        )

        self.old_resume_path = Path(self.application.resume_file.path)
        self.old_cover_path = Path(self.application.cover_letter_file.path)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.media_override.disable()
        self.media_temp_dir.cleanup()
        super().tearDown()

    def test_replacing_resume_removes_old_file(self):
        self.assertTrue(self.old_resume_path.exists())
        self.assertTrue(self.old_cover_path.exists())

        new_resume = SimpleUploadedFile(
            "new-resume.pdf",
            b"New resume content",
            content_type="application/pdf"
        )

        response = self.client.patch(
            reverse("application-detail", args=[self.application.id]),
            {"resume_file": new_resume},
            format="multipart"
        )

        self.assertEqual(response.status_code, 200)

        self.application.refresh_from_db()

        self.assertFalse(self.old_resume_path.exists())
        self.assertTrue(self.application.resume_file)
        self.assertTrue(Path(self.application.resume_file.path).exists())
        self.assertTrue(self.old_cover_path.exists())

class ApplicationCoverLetterReplacementAPITests(
    ApplicationFileReplacementAPITests
):

    def test_replacing_cover_letter_removes_old_file(self):
        self.assertTrue(self.old_cover_path.exists())
        self.assertTrue(self.old_resume_path.exists())

        new_cover_letter = SimpleUploadedFile(
            "new-cover-letter.pdf",
            b"New cover letter content",
            content_type="application/pdf"
        )

        response = self.client.patch(
            reverse("application-detail", args=[self.application.id]),
            {"cover_letter_file": new_cover_letter},
            format="multipart"
        )

        self.assertEqual(response.status_code, 200)

        self.application.refresh_from_db()

        self.assertFalse(self.old_cover_path.exists())
        self.assertTrue(self.application.cover_letter_file)
        self.assertTrue(
            Path(self.application.cover_letter_file.path).exists()
        )
        self.assertTrue(self.old_resume_path.exists())

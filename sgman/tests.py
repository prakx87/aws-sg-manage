from django.test import TestCase
from .models import SgAccess
from django.db.models import signals


class SgAccessTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        signals.pre_save.disconnect(sender=SgAccess, dispatch_uid="pre_save_sgaccess")
        signals.pre_save.disconnect(sender=SgAccess, dispatch_uid="pre_delete_sgaccess")

    def setUp(self) -> None:
        SgAccess.objects.create(
            sg_rule_id="sgr-0374f61bd244e0a96",
            allow_ip="10.80.1.0",
            datetime_added="2022-03-05 13:04:18.092996+00:00",
            added_by="admin",
        )
        SgAccess.objects.create(
            sg_rule_id="sgr-0234f3f2232aad470",
            allow_ip="10.80.1.2",
            datetime_added="2022-03-05 12:46:10.979092+00:00",
            added_by="raj",
        )

    def test_sg_access_allow_ip(self):
        admin = SgAccess.objects.get(sg_rule_id="sgr-0374f61bd244e0a96")
        raj = SgAccess.objects.get(sg_rule_id="sgr-0234f3f2232aad470")
        self.assertEqual(admin.allow_ip, "10.80.1.0")
        self.assertEqual(raj.allow_ip, "10.80.1.2")

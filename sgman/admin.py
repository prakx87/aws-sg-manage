from django.contrib import admin
from .models import VpnSgId, SgAccess


# Register your models here.
class VpnSgIdAdmin(admin.ModelAdmin):
    list_display = ('vpn_sg_id', 'vpn_sg_region')

    def has_add_permission(self, request):
        count = VpnSgId.objects.all().count()
        if count == 0:
            return True
        return False


class SgAccessAdmin(admin.ModelAdmin):
    list_display = ('sg_rule_id', 'allow_ip', 'datetime_added', 'added_by', 'enabled')


admin.site.register(VpnSgId, VpnSgIdAdmin)
admin.site.register(SgAccess, SgAccessAdmin)

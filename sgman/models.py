from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
import boto3

AWS_REGIONS = (
    ("us-east-1", "US-EAST-1"),
    ("us-west-1", "US-WEST-1")
)


class VpnSgId(models.Model):
    vpn_sg_id = models.CharField(max_length=50, null=False)
    vpn_sg_region = models.CharField(
        max_length=20,
        choices=AWS_REGIONS,
        default="us-east-1"
    )

    def __str__(self):
        return self.vpn_sg_id


class SgAccess(models.Model):
    sg_rule_id = models.CharField(max_length=50, null=True)
    employee_email = models.EmailField()
    allow_ip = models.GenericIPAddressField()
    datetime_added = models.DateTimeField(default=timezone.now)
    added_by = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.employee_email


@receiver(pre_save, sender=SgAccess, dispatch_uid="pre_save_sgaccess")
def pre_save_sgaccess(sender, instance: SgAccess, **kwargs):
    # Check if Security Group is added by checking Model entry count
    if VpnSgId.objects.count() != 1:
        raise Exception("Please add VPN Security group  and region first!!!")
    vpn_sg_id = VpnSgId.objects.values()[0]['vpn_sg_id']
    vpn_sg_region = VpnSgId.objects.values()[0]['vpn_sg_region']

    ec2client = boto3.client("ec2", region_name=vpn_sg_region)

    if instance._state.adding:
        # Add the new IP received from form in Security Group
        update_sg = ec2client.authorize_security_group_ingress(
            GroupId=vpn_sg_id,
            IpProtocol='TCP',
            CidrIp=instance.allow_ip + "/32",
            FromPort=80,
            ToPort=80,
        )

        # If IP is not added to Security group, raise exception
        if not update_sg['Return']:
            raise Exception("SG was not updated. Please check!!!")

        # Set Security Rule ID in Allow Access model
        instance.sg_rule_id = update_sg['SecurityGroupRules'][0]['SecurityGroupRuleId']
        instance.enabled = True
    else:
        # Remove IP using SG Rule ID received from form in Security Group
        remove_sg_entry = ec2client.revoke_security_group_ingress(
            GroupId=vpn_sg_id,
            SecurityGroupRuleIds=[instance.sg_rule_id],
        )
        if not remove_sg_entry['Return']:
            raise Exception("SG Entry was not Removed. Please check!!!")

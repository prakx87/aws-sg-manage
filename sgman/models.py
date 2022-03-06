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
    allow_ip = models.GenericIPAddressField(unique=True,)
    datetime_added = models.DateTimeField(default=timezone.now)
    added_by = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.allow_ip


@receiver(pre_save, sender=SgAccess, dispatch_uid="pre_save_sgaccess")
def pre_save_sgaccess(sender, instance: SgAccess, **kwargs):
    # Check if Security Group is added by checking Model entry count
    if VpnSgId.objects.count() != 1:
        raise Exception("Please add VPN Security group first!!!")
    vpn_sg_id = VpnSgId.objects.values()[0]['vpn_sg_id']
    vpn_sg_region = VpnSgId.objects.values()[0]['vpn_sg_region']

    ec2client = boto3.client("ec2", region_name=vpn_sg_region)
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


@receiver(pre_delete, sender=SgAccess, dispatch_uid="pre_delete_sgaccess")
def pre_delete_sgaccess(sender, instance: SgAccess, **kwargs):
    pass
from django.contrib import admin

from ahe_sys.models import Site, SiteMeta,  SiteDeviceList, Variable, FieldRule, ModeInput, \
    ModeInputOption, AllowedMode, SiteMetaConf, SiteVariableList, AheClient


@admin.register(AheClient)
class AheClientAdmin(admin.ModelAdmin):
    list_display = ('start_site_id', 'end_site_id', 'name')
    list_filter = ('start_site_id', 'end_site_id')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'name')
    list_filter = ('client',)

@admin.register(FieldRule)
class FieldRuleAdmin(admin.ModelAdmin):
    list_filter = ['rule_type']


@admin.register(AllowedMode)
class AllowedModeAdmin(admin.ModelAdmin):
    list_filter = ['site', 'mode']


@admin.register(ModeInput)
class ModeInputAdmin(admin.ModelAdmin):
    list_filter = ['mode']


@admin.register(ModeInputOption)
class ModeInputOptionAdmin(admin.ModelAdmin):
    list_filter = ['mode_input']


class MetaInline(admin.TabularInline):
    model = SiteMeta
    extra = 1


@admin.register(SiteMetaConf)
class SiteMetaConfAdmin(admin.ModelAdmin):
    list_display = ('site', 'version')
    list_filter = ('site', 'version')
    inlines = [MetaInline]


class VariableInline(admin.TabularInline):
    model = Variable
    extra = 1


@admin.register(SiteVariableList)
class SiteVariableConfAdmin(admin.ModelAdmin):
    list_display = ('site', 'version')
    list_filter = ('site', 'version')
    inlines = [VariableInline]

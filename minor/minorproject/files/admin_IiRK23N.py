import pycountry
import logging

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Q
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin as ModelAdmin
from imlib.django.management.commands._xlsformat import XlsFormat

from models import *

log = logging.getLogger(__name__)

pycountry_mapping = {
    'spanish': 'Spanish; Castilian',
    'greek': 'Greek, Modern (1453-)',
    'mandarin': 'Chinese'
}
pycountry_reverse_mapping = {
    'Spanish; Castilian': 'Spanish',
    'Greek, Modern (1453-)': 'Greek',
    'Chinese': 'Mandarin'
}


class CertificationResource(resources.ModelResource):
    """Import/export support for Certification"""
    name = fields.Field(column_name='Board Certification', attribute='name')
    doctors = fields.Field(column_name='NPI', attribute='doctors',
                           widget=widgets.ManyToManyWidget(model=Doctor, append=True))

    def clean_doctors(self, value):
        if isinstance(value, (str, unicode)):
            value = value.replace('-', '')
        if not isinstance(value, str):
            value = str(long(value))
        return value

    def clean_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value).strip()

    class Meta:
        model = Certification
        import_id_fields = ['name']
        use_transactions = False

class CertificationAdmin(ModelAdmin):
    resource_class = CertificationResource
    list_display = ('name', 'doctors_with_certification')

    def doctors_with_certification(self, obj):
        return self.doctors.all().count()
    doctors_with_certification.short_description = u'Doctors with Certification'
    
class AccreditationAdmin(ModelAdmin):
    model = Accreditation

class NetworkResource(resources.ModelResource):
    """Import/export support for Network"""
    network_id = fields.Field(column_name='network_id', attribute='network_id')
    name = fields.Field(column_name='network_name', attribute='name')
    tier = fields.Field(column_name='network_tier', attribute='tier')

    class Meta:
        model = Network
        import_id_fields = ['name', 'tier']
        exclude = ('create_dt', 'update_dt')
        skip_unchanged = False
        use_transactions = False

class NetworkAdmin(ModelAdmin):
    resource_class = NetworkResource
    list_display = ('pk', 'network_id', 'name', 'tier', 'doctors_in_network', 'groups_in_network',
                    'hospitals_in_network')
    list_filter = ('name',)

    def doctors_in_network(self, obj):
        return obj.doctors.all().count()
    doctors_in_network.short_description = u'Doctors in Network'

    def groups_in_network(self, obj):
        return obj.groups.all().count()
    groups_in_network.short_description = u'Groups in Network'

    def hospitals_in_network(self, obj):
        return obj.hospitals.all().count()
    hospitals_in_network.short_description = u'Hospitals in Network'


class SpecialtyResource(resources.ModelResource):
    """Import/export support for Specialty (Doctors and Groups Only)"""
    code = fields.Field(column_name='specialty_code', attribute='code')
    sub_code = fields.Field(column_name='subspecialty_code', attribute='sub_code')
    name = fields.Field(column_name='provider_specialty', attribute='name')

    def clean_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value).strip()

    def clean_sub_code(self, value):
        return value or ''

    def get_instance(self, instance_loader, row):
        return super(SpecialtyResource, self).get_instance(instance_loader, row)

    class Meta:
        model = Specialty
        import_id_fields = ['code', 'sub_code']
        skip_unchanged = False
        use_transactions = False

class SpecialtyAdmin(ModelAdmin):
    resource_class = SpecialtyResource
    list_display = ('pk', 'code', 'sub_code', '__unicode__')
    search_fields = ('code', 'sub_code', 'name')
    ordering = ('name',)


class HospitalSpecialtyResource(resources.ModelResource):
    """Import/export support for Specialty (Hospitals Only)"""
    name = fields.Field(column_name='provider_specialty', attribute='name')

    def clean_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value).strip()

    class Meta:
        model = HospitalSpecialty
        import_id_fields = ['name']
        skip_unchanged = False
        use_transactions = False

class HospitalSpecialtyAdmin(ModelAdmin):
    resource_class = SpecialtyResource
    list_display = ('pk', '__unicode__')
    search_fields = ('name',)


class LocationResource(resources.ModelResource):
    """Import/export support for Location"""
    name = fields.Field(column_name='facility_name', attribute='name')
    telephone = fields.Field(column_name='facility_telephone', attribute='telephone')
    fax = fields.Field(column_name='facility_fax', attribute='fax')
    address = fields.Field(column_name='facility_address1', attribute='address')
    city = fields.Field(column_name='facility_city', attribute='city')
    state = fields.Field(column_name='facility_state', attribute='state')
    zip = fields.Field(column_name='facility_zip', attribute='zip')
    longitude = fields.Field(column_name='facility_longitude', attribute='longitude')
    latitude = fields.Field(column_name='facility_latitude', attribute='latitude')

    def clean_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value).strip()

    def clean_telephone(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.phone(value, default='').strip()

    def clean_fax(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.phone(value, default='').strip()

    def clean_address(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.street_address(value).strip()

    def clean_city(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value).strip()

    def clean_state(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.state(value).strip()

    def clean_zip(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.zipcode(value).strip()

    def after_save_instance(self, instance, dry_run):
        """Post-save: geocode new or modified addresses"""
        pass

    class Meta:
        model = Location
        import_id_fields = ['name', 'address', 'city', 'state', 'zip']
        skip_unchanged = False
        use_transactions = True
        exclude = ('create_dt', 'update_dt')

class LocationAdmin(ModelAdmin):
    resource_class = LocationResource
    list_display = ('pk', 'name', 'address', 'city', 'state', 'zip', 'telephone', 'fax', 'latitude', 'longitude')


class LanguageAdmin(ModelAdmin):
    # resource_class = LanguageResource
    list_display = ('code', 'code2', 'name')
    list_filter = ('code', 'name')


class HospitalResource(resources.ModelResource):
    npi = fields.Field(column_name='npi', attribute='npi')
    name = fields.Field(column_name='facility_name', attribute='name')
    locations = fields.NaturalForeignKeyField(resource=LocationResource(), attribute='locations',
                                              widget=widgets.NaturalManyToManyWidget(model=Location))
    specialty = fields.NaturalForeignKeyField(resource=HospitalSpecialtyResource(), attribute='specialty',
                                              widget=widgets.NaturalForeignKeyWidget(model=HospitalSpecialty))
    northern = fields.Field(column_name='Northern')
    southern = fields.Field(column_name='Southern')

    def skip_row(self, row):
        return not bool(row.get('npi'))

    def get_instance(self, instance_loader, row):
        super(HospitalResource, self).get_instance(instance_loader=instance_loader, row=row)
        self._northern = row.get(self.fields['northern'].column_name)
        self._southern = row.get(self.fields['southern'].column_name)

    def after_save_instance(self, instance, dry_run):
        if not dry_run:
            if self._northern and self._northern.lower() == u'northern':
                network = Network.objects.get(name='Northern Simple Network')
                instance.networks.add(network)
                network = Network.objects.get(name='Frontier Simple Network')
                instance.networks.add(network)
            if self._southern and self._southern.lower() == u'southern':
                network = Network.objects.get(name='Southern Simple Network')
                instance.networks.add(network)
                network = Network.objects.get(name='Neighborhood VIP Network', tier='Tier 1')
                instance.networks.add(network)
                network = Network.objects.get(name='Star Network', tier='Tier 1')
                instance.networks.add(network)

    class Meta:
        model = Hospital
        import_id_fields = ['npi']  # Use npi for pk
        skip_unchanged = False
        use_transactions = False
        exclude = ('create_dt', 'update_dt')

class HospitalAdmin(ModelAdmin):
    resource_class = HospitalResource
    list_display = ('npi', 'name', 'get_specialty', 'get_locations', 'get_networks')
    list_filter = ('specialty', 'networks')
    search_fields = ('npi', 'name')
    filter_horizontal = ('locations', 'networks')
    ordering = ('specialty__name', 'name')

    def get_specialty(self, obj):
        return u'%s' % obj.specialty.name

    def get_locations(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_location_change', args=(l.pk,)), l.pk)
                         for l in obj.locations.all()])
    get_locations.allow_tags = True
    get_locations.short_description = u'Locations'

    def get_networks(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_network_change', args=(n.pk,)), n.pk)
                          for n in obj.networks.all()])
    get_networks.allow_tags = True
    get_networks.short_description = u'Networks'

    def get_doctors(self, obj):
        return u'%s' % obj.doctors.all().count()


class GroupResource(resources.ModelResource):
    npi = fields.Field(column_name='group_npi', attribute='npi')
    name = fields.Field(column_name='facility_name', attribute='name')
    locations = fields.NaturalForeignKeyField(resource=LocationResource(), attribute='locations',
                                              widget=widgets.NaturalManyToManyWidget(model=Location))
    specialties = fields.NaturalForeignKeyField(resource=SpecialtyResource(), attribute='specialties',
                                                widget=widgets.NaturalManyToManyWidget(
                                                    model=Specialty, allowed_empty=['sub_code']))
    networks = fields.NaturalForeignKeyField(resource=NetworkResource(), attribute='networks',
                                             widget=widgets.NaturalManyToManyWidget(
                                                 model=Network, allowed_empty=['tier']))
    language1 = fields.Field(column_name='language_spoken1')
    language2 = fields.Field(column_name='language_spoken2')
    language3 = fields.Field(column_name='language_spoken3')
    language4 = fields.Field(column_name='language_spoken4')

    def get_instance(self, instance_loader, row):
        super(GroupResource, self).get_instance(instance_loader=instance_loader, row=row)
        self._language1 = row.get(self.fields['language1'].column_name)
        self._language2 = row.get(self.fields['language2'].column_name)
        self._language3 = row.get(self.fields['language3'].column_name)
        self._language4 = row.get(self.fields['language4'].column_name)

    def before_save_instance(self, instance, dry_run):
        xlsfmt = XlsFormat()
        self._languages = []
        for language_key in ['_language1', '_language2', '_language3', '_language4']:
            language_list = getattr(self, language_key, '')
            if language_list:
                self._languages += [xlsfmt.title(l) for l in language_list.split(',') if l]
        if 'English' not in self._languages:
            self._languages.insert(0, 'English')

    def after_save_instance(self, instance, dry_run):
        xlsfmt = XlsFormat()
        if not dry_run:
            for language_name in self._languages:
                language, created = Language.objects.get_or_create(name=xlsfmt.title(language_name))
                instance.languages.add(language)
                # try:
                #     pylanguage = pycountry.languages.get(name=xlsfmt.title(pycountry_mapping.get(language.lower(),
                #                                                                                  language)))
                # except KeyError:
                #     log.warning('Unable to find language %s' % language)
                # else:
                #     language, created = Language.objects.get_or_create(code=pylanguage.bibliographic,
                #                                                        defaults={'code2': pylanguage.alpha2,
                #                                                                  'name': pylanguage.name})
                #     instance.languages.add(language)
        self._language1 = self._language2 = self._language3 = self._language4 = self._languages = None

    def __init__(self, *args, **kwargs):
        super(GroupResource, self).__init__(*args, **kwargs)
        self.hospital_npis = [h.npi for h in Hospital.objects.all()]

    def skip_row(self, row):
        npi = row.get('group_npi', '')
        if isinstance(npi, (str, unicode)):
            npi = npi.replace('-', '').strip()
        return (not bool(npi)) or npi in self.hospital_npis

    def clean_npi(self, value):
        if isinstance(value, (str, unicode)):
            value = value.replace('-', '')
        return long(value)

    def clean_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value)

    class Meta:
        model = Group
        import_id_fields = ['npi']  # Use npi for pk
        skip_unchanged = False
        use_transactions = False
        exclude = ('create_dt', 'update_dt')

class GroupAdmin(ModelAdmin):
    resource_class = GroupResource
    list_display = ('npi', '__unicode__', 'doctors_in_group', 'get_specialties', 'get_locations', 'get_languages',
                    'get_networks')
    search_fields = ('npi', 'name')
    ordering = ('name',)
    filter_horizontal = ('specialties', 'locations', 'languages', 'networks')

    def get_locations(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_location_change', args=(l.pk,)), l.pk)
                         for l in obj.locations.all()])
    get_locations.allow_tags = True
    get_locations.short_description = u'Locations'

    def get_specialties(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_specialty_change', args=(s.pk,)), s.pk)
                         for s in obj.specialties.all()])
    get_specialties.allow_tags = True
    get_specialties.short_description = u'Specialties'

    def get_languages(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_language_change', args=(l.pk,)), l.pk)
                         for l in obj.languages.all()])
    get_languages.allow_tags = True
    get_languages.short_description = u'Languages'

    def get_networks(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_network_change', args=(n.pk,)), n.pk)
                          for n in obj.networks.all()])
    get_networks.allow_tags = True
    get_networks.short_description = u'Networks'

    def doctors_in_group(self, obj):
        return obj.doctors.all().count()
    doctors_in_group.short_description = u'Doctors in Group'


class DoctorResource(resources.ModelResource):
    """Import/export support for Doctor"""
    npi = fields.Field(column_name='provider_npi', attribute='npi')
    first_name = fields.Field(column_name='provider_first_name', attribute='firstname')
    middle_name = fields.Field(column_name='provider_middle_name', attribute='middlename')
    last_name = fields.Field(column_name='provider_last_name', attribute='lastname')
    suffix = fields.Field(column_name='provider_suffix', attribute='suffix')
    gender = fields.Field(column_name='provider_gender', attribute='gender')
    #degree = fields.Field(column_name='provider_degree', attribute='degree')
    degree = fields.NaturalForeignKeyField(resource=DegreeResource(),attribute='degreerecid'
                                              widget=widgets.NaturalManyToManyWidget(model=Degrees))
    #locations = fields.NaturalForeignKeyField(resource=LocationResource(), attribute='locations',
    #                                          widget=widgets.NaturalManyToManyWidget(model=Location))
    businessaddress1 = fields.Field(column_name='provider_address1',attribute='businessaddress1')
    businessaddress2 = fields.Field(column_name='provider_address2',attribute='businessaddress2')
    businesscity = fields.Field(column_name='provider_city',attribute='businesscity')
    #businesscounty = fields.Field(column_name='provider_county',attribute='businesscounty')
    businessstateid - fields.NaturalForeignKeyField(resource=State(),attribute='businessstateid'
                                                      widget=widgets.NaturalManyToManyWidget(model=States)) 
    businesszip = fields.Field(column_name='provider_zip',attribute='businesszip')
    businessfax = fields.Field(column_name='provider_fax',attribute='businessfax')
    businessphone = fields.Field(column_name='provider_phone',attribute='businessphone') 
    networks = fields.NaturalForeignKeyField(resource=NetworkResource(), attribute='networks',
                                             widget=widgets.NaturalManyToManyWidget(model=Network,
                                                                                    allowed_empty=['tier']))
    specialties = fields.NaturalForeignKeyField(resource=SpecialtyResource(), attribute='specialties',
                                                widget=widgets.NaturalManyToManyWidget(
                                                    model=Specialty, allowed_empty=['sub_code']))
    groups = fields.Field(column_name='group_npi', attribute='groups',
                          widget=widgets.ManyToManyWidget(model=Group, append=True))
    # hospitals = fields.Field(column_name='group_npi', attribute='hospitals',
    #                          widget=widgets.ManyToManyWidget(model=Hospital, append=True))
    language1 = fields.Field(column_name='language_spoken1')
    language2 = fields.Field(column_name='language_spoken2')
    language3 = fields.Field(column_name='language_spoken3')
    language4 = fields.Field(column_name='language_spoken4')

    def get_instance(self, instance_loader, row):
        super(DoctorResource, self).get_instance(instance_loader=instance_loader, row=row)
        self._language1 = row.get(self.fields['language1'].column_name, '')
        self._language2 = row.get(self.fields['language2'].column_name, '')
        self._language3 = row.get(self.fields['language3'].column_name, '')
        self._language4 = row.get(self.fields['language4'].column_name, '')

    def before_save_instance(self, instance, dry_run):
        xlsfmt = XlsFormat()
        self._languages = []
        for language_key in ['_language1', '_language2', '_language3', '_language4']:
            languages = getattr(self, language_key, '') or ''
            self._languages += [xlsfmt.title(l) for l in languages.split(',') if l]
        if 'English' not in self._languages:
            self._languages.insert(0, 'English')

    def after_save_instance(self, instance, dry_run):
        xlsfmt = XlsFormat()
        if not dry_run:
            for language_name in self._languages:
                language, created = Language.objects.get_or_create(name=xlsfmt.title(language_name))
                instance.languages.add(language)
                # TODO: Disabling pycountry for now because it doesn't use common names for languages.
                # try:
                #     pylanguage = pycountry.languages.get(name=xlsfmt.title(pycountry_mapping.get(language.lower(),
                #                                                                                  language)))
                # except KeyError:
                #     log.warning('Unable to find language %s' % language)
                # else:
                #     language, created = Language.objects.get_or_create(code=pylanguage.bibliographic,
                #                                                        defaults={'code2': pylanguage.alpha2,
                #                                                                  'name': pylanguage.name})
                #     instance.languages.add(language)

    def skip_row(self, row):
        return not bool(row.get('provider_npi'))

    def clean_npi(self, value):
        if isinstance(value, (str, unicode)):
            value = value.replace('-', '')
        return long(value)

    def clean_first_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value)

    def clean_middle_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value)

    def clean_last_name(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.title(value)

    def clean_degree(self, value):
        xlsfmt = XlsFormat()
        return xlsfmt.doctor_degree(value)

    def clean_groups(self, value):
        if isinstance(value, (str, unicode)):
            value = value.replace('-', '')
        if not isinstance(value, str):
            value = str(long(value))
        return value

    class Meta:
        model = Doctor
        import_id_fields = ['npi']  # Use npi for pk
        skip_unchanged = False
        use_transactions = False
        exclude = ('create_dt', 'update_dt')

class DoctorAdmin(ModelAdmin):
    resource_class = DoctorResource
    list_display = ('npi', '__unicode__', 'degree', 'get_specialties', 'get_networks', 'get_locations',
                    'get_languages', 'get_groups', 'get_hospitals', 'get_networks', 'get_certifications')
    search_fields = ('npi', 'first_name', 'last_name')
    filter_horizontal = ('specialties', 'groups', 'locations', 'languages', 'certifications', 'credentials',
                         'networks', 'hospitals')
    ordering = ('last_name', 'first_name', 'middle_name')

    def get_networks(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_network_change', args=(n.pk,)), n.pk)
                         for n in obj.networks.all()])
    get_networks.allow_tags = True
    get_networks.short_description = u'Networks'

    def get_locations(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_location_change', args=(l.pk,)), l.pk)
                         for l in obj.locations.all()])
    get_locations.allow_tags = True
    get_locations.short_description = u'Locations'

    def get_specialties(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_specialty_change', args=(s.pk,)), s.pk)
                         for s in obj.specialties.all()])
    get_specialties.allow_tags = True
    get_specialties.short_description = u'Specialties'

    def get_languages(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_language_change', args=(l.pk,)), l.pk)
                         for l in obj.languages.all()])
    get_languages.allow_tags = True
    get_languages.short_description = u'Languages'

    def get_groups(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_group_change', args=(g.pk,)), g.pk)
                         for g in obj.groups.all()])
    get_groups.allow_tags = True
    get_groups.short_description = u'Groups'

    def get_hospitals(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_hospital_change', args=(h.pk,)), h.pk)
                         for h in obj.hospitals.all()])
    get_hospitals.allow_tags = True
    get_hospitals.short_description = u'Hospitals'

    def get_certifications(self, obj):
        return u', '.join([u'<a href="%s">%s</a>' % (reverse('admin:doctors_certification_change', args=(c.pk,)), c.pk)
                         for c in obj.certifications.all()])
    get_certifications.allow_tags = True
    get_certifications.short_description = 'Certifications'


class DoctorHospitalsResource(resources.ModelResource):
    hospital_id = fields.Field(column_name='hospital_npi', attribute='hospital_id')
    doctor_id = fields.Field(column_name='doctor_npi', attribute='doctor_id')

    def clean_hospital_npi(self, value):
        if isinstance(value, (str, unicode)):
            value = value.replace('-', '')
        return long(value)

    def clean_doctor_id(self, value):
        if isinstance(value, (str, unicode)):
            value = value.replace('-', '')
        return long(value)

    def skip_row(self, row):
        return not (bool(row.get('hospital_npi'))
                    and Hospital.objects.filter(npi=self.clean_doctor_id(row.get('hospital_npi'))).exists()
                    and bool(row.get('doctor_npi'))
                    and Doctor.objects.filter(npi=self.clean_doctor_id(row.get('doctor_npi'))).exists())

    class Meta:
        model = DoctorHospitals
        import_id_fields = ['hospital_id', 'doctor_id']

class DoctorHospitalsAdmin(ModelAdmin):
    resource_class = DoctorHospitalsResource


admin.site.register(Network, NetworkAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(HospitalSpecialty, HospitalSpecialtyAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(DoctorHospitals, DoctorHospitalsAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Accreditation, AccreditationAdmin)

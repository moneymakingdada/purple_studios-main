from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Apply a purple-branded theme to django-admin-interface."

    def handle(self, *args, **options):
        from admin_interface.models import Theme

        theme, _ = Theme.objects.get_or_create(name="Purple")
        theme.title = "Purple Admin"
        theme.title_visible = True
        theme.logo_visible = False
        theme.css_header_background_color = "#1D0730"
        theme.css_header_text_color = "#FAF7F4"
        theme.css_header_link_color = "#E9CE7D"
        theme.css_header_link_hover_color = "#D4AF37"
        theme.css_module_background_color = "#2B0A3D"
        theme.css_module_text_color = "#FAF7F4"
        theme.css_module_link_color = "#E9CE7D"
        theme.css_module_link_hover_color = "#D4AF37"
        theme.css_module_rounded_corners = True
        theme.css_generic_link_color = "#6C2BD9"
        theme.css_generic_link_hover_color = "#B24BF3"
        theme.css_save_button_background_color = "#6C2BD9"
        theme.css_save_button_background_hover_color = "#B24BF3"
        theme.css_save_button_text_color = "#FFFFFF"
        theme.css_delete_button_background_color = "#c0392b"
        theme.css_delete_button_background_hover_color = "#a93226"
        theme.list_filter_dropdown = True
        theme.related_modal_active = True
        theme.env_name = "Production"
        theme.env_color = "#D4AF37"
        theme.env_visible_in_header = True
        theme.active = True
        theme.save()

        self.stdout.write(self.style.SUCCESS("Purple admin theme applied and activated."))

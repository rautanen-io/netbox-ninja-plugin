from core.models import ObjectType
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from netbox_ninja_plugin.api.serializers import (
    NinjaTemplateSerializer,
    NinjaTemplateStringFilterOptionSerializer,
    NinjaTemplateStringFilterSerializer,
)
from netbox_ninja_plugin.ninja_template.choices import NinjaTemplateOutputTypeChoices
from netbox_ninja_plugin.ninja_template.models import (
    NinjaTemplate,
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
)


class NinjaTemplateViewSet(NetBoxModelViewSet):
    queryset = NinjaTemplate.objects.all()
    serializer_class = NinjaTemplateSerializer


class NinjaTemplateStringFilterViewSet(NetBoxModelViewSet):
    queryset = NinjaTemplateStringFilter.objects.all()
    serializer_class = NinjaTemplateStringFilterSerializer


class NinjaTemplateStringFilterOptionViewSet(NetBoxModelViewSet):
    queryset = NinjaTemplateStringFilterOption.objects.all()
    serializer_class = NinjaTemplateStringFilterOptionSerializer


class NinjaRenderView(APIView):

    queryset = NinjaTemplate.objects.all()

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        # ?app=dcim&model=site&pk=1

        ninja_template_id = pk
        target_object = None
        target_object_type = None
        target_object_id = None

        try:
            app = request.GET.get("app")
            model = request.GET.get("model")
            target_object_type = ObjectType.objects.get(app_label=app, model=model)
            model_class = target_object_type.model_class()
            target_object_id = request.GET.get("pk")
            target_object = get_object_or_404(model_class, pk=target_object_id)
        except ObjectType.DoesNotExist as exc:
            raise Http404("Requested object type not found") from exc
        except Http404:
            # Preserve the original 404 semantics/messages from get_object_or_404.
            raise
        except Exception as exc:
            raise Http404("Requested target object not found") from exc

        # Use standard permission codename and object-level check
        perm_codename = (
            f"{target_object_type.app_label}.view_{target_object_type.model}"
        )
        if not request.user.has_perm(perm_codename, target_object):
            raise PermissionDenied("You do not have permission to view this object.")

        ninja_template = get_object_or_404(NinjaTemplate, pk=ninja_template_id)
        ninja_template_object_type = ObjectType.objects.get_for_model(NinjaTemplate)
        template_object_types_exist = ninja_template.object_types.exists()

        # Check that if the template doesn't have any object types, template
        # can only be rendered to a NinjaTemplate object type:
        unassigned_ninja_template = False
        if (
            not template_object_types_exist
            and target_object_type == ninja_template_object_type
            and str(target_object_id) == str(ninja_template_id)
        ):
            unassigned_ninja_template = True

        # Check that the selected template is applied to this object type:
        is_applied_to_object_type = ninja_template.object_types.filter(
            pk=target_object_type.pk
        ).exists()
        if not unassigned_ninja_template and not is_applied_to_object_type:
            raise Http404(f"Selected template is not applied to {target_object_type}.")

        data, status = ninja_template.render(**{"target_object": target_object})
        http_content_type = "text/plain"
        if ninja_template.output_type == NinjaTemplateOutputTypeChoices.JSON:
            http_content_type = "application/json"
        elif ninja_template.output_type == NinjaTemplateOutputTypeChoices.DRAW_IO:
            http_content_type = "image/svg+xml"

        return HttpResponse(data, http_content_type, 200 if status else 400)

from app.schemas.status import StatusCreate, StatusUpdate, StatusPatch
import re
from app.core.errors import ValidationError


class StatusCreateValidator:
    def validate_status_name(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.name.strip() == "":
            raise ValidationError("Name is required")
        if len(status.name) > 100:
            raise ValidationError("Name must be less than 100 characters")
        return status

    def validate_status_color(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.color.strip() == "":
            raise ValidationError("Color is required")
        if status.color[0] != "#":
            raise ValidationError("Color must start with #")
        if len(status.color) > 7:
            raise ValidationError("Color must be less than 7 characters long")
        if not re.match(r"^#[0-9a-fA-F]{6}$", status.color):
            raise ValidationError("Color must be a valid hex color")
        return status

    def validate_status_icon(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.icon.strip() == "":
            raise ValidationError("Icon is required")
        if len(status.icon) > 100:
            raise ValidationError("Icon must be less than 100 characters")
        return status

    def validate_status_order(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.order <= 0:
            raise ValidationError("Order must be greater than 0")
        return status

    def validate_status(status: StatusCreate) -> StatusCreate:
        status = StatusCreateValidator.validate_status_name(status)
        status = StatusCreateValidator.validate_status_color(status)
        status = StatusCreateValidator.validate_status_icon(status)
        status = StatusCreateValidator.validate_status_order(status)
        return status


class StatusUpdateValidator:
    def validate_status_name(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.name.strip() == "":
            raise ValidationError("Name is required")
        if len(status.name) > 100:
            raise ValidationError("Name must be less than 100 characters")
        return status

    def validate_status_color(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.color.strip() == "":
            raise ValidationError("Color is required")
        if status.color[0] != "#":
            raise ValidationError("Color must start with #")
        if len(status.color) > 7:
            raise ValidationError("Color must be less than 7 characters long")
        if not re.match(r"^#[0-9a-fA-F]{6}$", status.color):
            raise ValidationError("Color must be a valid hex color")
        return status

    def validate_status_icon(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.icon.strip() == "":
            raise ValidationError("Icon is required")
        if len(status.icon) > 100:
            raise ValidationError("Icon must be less than 100 characters")
        return status

    def validate_status_order(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.order <= 0:
            raise ValidationError("Order must be greater than 0")
        return status

    def validate_status(status: StatusUpdate) -> StatusUpdate:
        status = StatusUpdateValidator.validate_status_name(status)
        status = StatusUpdateValidator.validate_status_color(status)
        status = StatusUpdateValidator.validate_status_icon(status)
        status = StatusUpdateValidator.validate_status_order(status)
        return status


class StatusPatchValidator:
    def validate_status_name(
        status: StatusPatch,
    ) -> StatusPatch:
        if status.name is not None:
            if status.name.strip() == "":
                raise ValidationError("Name is required")
            if len(status.name) > 100:
                raise ValidationError("Name must be less than 100 characters")
        return status

    def validate_status_color(
        status: StatusPatch,
    ) -> StatusPatch:
        if status.color is not None:
            if status.color.strip() == "":
                raise ValidationError("Color is required")
            if status.color[0] != "#":
                raise ValidationError("Color must start with #")
            if len(status.color) > 7:
                raise ValidationError("Color must be less than 7 characters long")
            if not re.match(r"^#[0-9a-fA-F]{6}$", status.color):
                raise ValidationError("Color must be a valid hex color")
            return status

    def validate_status_icon(
        status: StatusPatch,
    ) -> StatusPatch:
        if status.icon is not None:
            if status.icon.strip() == "":
                raise ValidationError("Icon is required")
            if len(status.icon) > 100:
                raise ValidationError("Icon must be less than 100 characters")
            return status

    def validate_status_order(
        status: StatusPatch,
    ) -> StatusPatch:
        if status.order is not None:
            if status.order <= 0:
                raise ValidationError("Order must be greater than 0")
            return status

    def validate_status(status: StatusPatch) -> StatusPatch:
        status = StatusPatchValidator.validate_status_name(status)
        status = StatusPatchValidator.validate_status_color(status)
        status = StatusPatchValidator.validate_status_icon(status)
        status = StatusPatchValidator.validate_status_order(status)
        return status

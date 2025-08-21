from app.schemas.status import StatusCreate, StatusUpdate, StatusPatch
import re
from app.core.errors import ValidationError


class StatusCreateValidator:
    def validate_status_name(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.name.strip() == "":
            raise ValueError("Name is required")
        if len(status.name) > 100:
            raise ValueError("Name must be less than 100 characters")

    def validate_status_color(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.color.strip() == "":
            raise ValueError("Color is required")
        if status.color[0] != "#":
            raise ValueError("Color must start with #")
        if len(status.color) > 7:
            raise ValueError("Color must be less than 7 characters long")
        if not re.match(r"^#[0-9a-fA-F]{6}$", status.color):
            raise ValueError("Color must be a valid hex color")
        return status

    def validate_status_icon(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.icon.strip() == "":
            raise ValueError("Icon is required")
        if len(status.icon) > 100:
            raise ValueError("Icon must be less than 100 characters")
        return status

    def validate_status_order(
        status: StatusCreate,
    ) -> StatusCreate:
        if status.order <= 0:
            raise ValueError("Order must be greater than 0")
        return status

    def validate_status_user_key(
        status: StatusCreate, user_key: str
    ) -> StatusCreate:
        if status.user_key != user_key:
            raise ValueError("User key is not valid")
        return status

    def validate_status_description(status: StatusCreate) -> StatusCreate:
        if status.description is not None:
            if len(status.description) > 1000:
                raise ValueError("Description must be less than 1000 characters")
        return status

    def validate_status(status: StatusCreate, user_key: str) -> StatusCreate:
        try:
            StatusCreateValidator.validate_status_name(status)
            StatusCreateValidator.validate_status_color(status)
            StatusCreateValidator.validate_status_icon(status)
            StatusCreateValidator.validate_status_order(status)
            StatusCreateValidator.validate_status_user_key(status, user_key)
            return status
        except ValueError as e:
            # Pass the error message as a string, not the entire exception object
            raise ValidationError(custom_message=str(e))


class StatusUpdateValidator:
    def validate_status_name(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.name.strip() == "":
            raise ValueError("Name is required")
        if len(status.name) > 100:
            raise ValueError("Name must be less than 100 characters")

    def validate_status_color(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.color.strip() == "":
            raise ValueError("Color is required")
        if status.color[0] != "#":
            raise ValueError("Color must start with #")
        if len(status.color) > 7:
            raise ValueError("Color must be less than 7 characters long")
        if not re.match(r"^#[0-9a-fA-F]{6}$", status.color):
            raise ValueError("Color must be a valid hex color")
        return status

    def validate_status_icon(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.icon.strip() == "":
            raise ValueError("Icon is required")
        if len(status.icon) > 100:
            raise ValueError("Icon must be less than 100 characters")
        return status

    def validate_status_order(
        status: StatusUpdate,
    ) -> StatusUpdate:
        if status.order <= 0:
            raise ValueError("Order must be greater than 0")
        return status

    def validate_status(status: StatusUpdate) -> StatusUpdate:
        try:
            StatusUpdateValidator.validate_status_name(status)
            StatusUpdateValidator.validate_status_color(status)
            StatusUpdateValidator.validate_status_icon(status)
            StatusUpdateValidator.validate_status_order(status)
            return status
        except ValueError as e:
            raise ValidationError(custom_message=str(e))


class StatusPatchValidator:
    def validate_status_name(
            status: StatusPatch,
    ) -> StatusPatch:
        if status.name is not None:
            if status.name.strip() == "":
                raise ValueError("Name is required")
            if len(status.name) > 100:
                raise ValueError("Name must be less than 100 characters")

    def validate_status_color(
        status: StatusPatch,
    ) -> StatusPatch:
        if status.color is not None:
            if status.color.strip() == "":
                raise ValueError("Color is required")
            if status.color[0] != "#":
                raise ValueError("Color must start with #")
            if len(status.color) > 7:
                raise ValueError("Color must be less than 7 characters long")
            if not re.match(r"^#[0-9a-fA-F]{6}$", status.color):
                raise ValueError("Color must be a valid hex color")
            return status

    def validate_status_icon(
        status: StatusPatch,
    ) -> StatusPatch:
        if status.icon is not None:
            if status.icon.strip() == "":
                raise ValueError("Icon is required")
            if len(status.icon) > 100:
                raise ValueError("Icon must be less than 100 characters")
            return status

    def validate_status_order(
        status: StatusPatch,
    ) -> StatusPatch:
        if status.order is not None:
            if status.order <= 0:
                raise ValueError("Order must be greater than 0")
            return status

    def validate_status(status: StatusPatch) -> StatusPatch:
        try:
            StatusPatchValidator.validate_status_name(status)
            StatusPatchValidator.validate_status_color(status)
            StatusPatchValidator.validate_status_icon(status)
            StatusPatchValidator.validate_status_order(status)
            return status
        except ValueError as e:
            raise ValidationError(custom_message=str(e))

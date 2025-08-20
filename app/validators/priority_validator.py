from app.schemas.priority import PriorityCreate, PriorityUpdate, PriorityPatch
import re
from app.core.errors import ValidationError


class PriorityCreateValidator:
    def validate_priority_name(
        priority: PriorityCreate,
    ) -> PriorityCreate:
        if priority.name.strip() == "":
            raise ValueError("Name is required")
        if len(priority.name) > 100:
            raise ValueError("Name must be less than 100 characters")

    def validate_priority_color(
        priority: PriorityCreate,
    ) -> PriorityCreate:
        if priority.color.strip() == "":
            raise ValueError("Color is required")
        if priority.color[0] != "#":
            raise ValueError("Color must start with #")
        if len(priority.color) > 7:
            raise ValueError("Color must be less than 7 characters long")
        if not re.match(r"^#[0-9a-fA-F]{6}$", priority.color):
            raise ValueError("Color must be a valid hex color")
        return priority

    def validate_priority_icon(
        priority: PriorityCreate,
    ) -> PriorityCreate:
        if priority.icon.strip() == "":
            raise ValueError("Icon is required")
        if len(priority.icon) > 100:
            raise ValueError("Icon must be less than 100 characters")
        return priority

    def validate_priority_order(
        priority: PriorityCreate,
    ) -> PriorityCreate:
        if priority.order <= 0:
            raise ValueError("Order must be greater than 0")
        return priority

    def validate_priority_user_key(
        priority: PriorityCreate, user_key: str
    ) -> PriorityCreate:
        if priority.user_key != user_key:
            raise ValueError("User key is not valid")
        return priority

    def validate_priority_description(priority: PriorityCreate) -> PriorityCreate:
        if priority.description is not None:
            if len(priority.description) > 1000:
                raise ValueError("Description must be less than 1000 characters")
        return priority

    def validate_priority(priority: PriorityCreate, user_key: str) -> PriorityCreate:
        try:
            PriorityCreateValidator.validate_priority_name(priority)
            PriorityCreateValidator.validate_priority_color(priority)
            PriorityCreateValidator.validate_priority_icon(priority)
            PriorityCreateValidator.validate_priority_order(priority)
            PriorityCreateValidator.validate_priority_user_key(priority, user_key)
            return priority
        except ValueError as e:
            # Pass the error message as a string, not the entire exception object
            raise ValidationError(custom_message=str(e))


class PriorityUpdateValidator:
    def validate_priority_name(
        priority: PriorityUpdate,
    ) -> PriorityUpdate:
        if priority.name.strip() == "":
            raise ValueError("Name is required")
        if len(priority.name) > 100:
            raise ValueError("Name must be less than 100 characters")

    def validate_priority_color(
        priority: PriorityUpdate,
    ) -> PriorityUpdate:
        if priority.color.strip() == "":
            raise ValueError("Color is required")
        if priority.color[0] != "#":
            raise ValueError("Color must start with #")
        if len(priority.color) > 7:
            raise ValueError("Color must be less than 7 characters long")
        if not re.match(r"^#[0-9a-fA-F]{6}$", priority.color):
            raise ValueError("Color must be a valid hex color")
        return priority

    def validate_priority_icon(
        priority: PriorityUpdate,
    ) -> PriorityUpdate:
        if priority.icon.strip() == "":
            raise ValueError("Icon is required")
        if len(priority.icon) > 100:
            raise ValueError("Icon must be less than 100 characters")
        return priority

    def validate_priority_order(
        priority: PriorityUpdate,
    ) -> PriorityUpdate:
        if priority.order <= 0:
            raise ValueError("Order must be greater than 0")
        return priority

    def validate_priority(priority: PriorityUpdate) -> PriorityUpdate:
        try:
            PriorityUpdateValidator.validate_priority_name(priority)
            PriorityUpdateValidator.validate_priority_color(priority)
            PriorityUpdateValidator.validate_priority_icon(priority)
            PriorityUpdateValidator.validate_priority_order(priority)
            return priority
        except ValueError as e:
            raise ValidationError(custom_message=str(e))


class PriorityPatchValidator:
    def validate_priority_name(
        priority: PriorityPatch,
    ) -> PriorityPatch:
        if priority.name is not None:
            if priority.name.strip() == "":
                raise ValueError("Name is required")
            if len(priority.name) > 100:
                raise ValueError("Name must be less than 100 characters")

    def validate_priority_color(
        priority: PriorityPatch,
    ) -> PriorityPatch:
        if priority.color is not None:
            if priority.color.strip() == "":
                raise ValueError("Color is required")
            if priority.color[0] != "#":
                raise ValueError("Color must start with #")
            if len(priority.color) > 7:
                raise ValueError("Color must be less than 7 characters long")
            if not re.match(r"^#[0-9a-fA-F]{6}$", priority.color):
                raise ValueError("Color must be a valid hex color")
            return priority

    def validate_priority_icon(
        priority: PriorityPatch,
    ) -> PriorityPatch:
        if priority.icon is not None:
            if priority.icon.strip() == "":
                raise ValueError("Icon is required")
            if len(priority.icon) > 100:
                raise ValueError("Icon must be less than 100 characters")
            return priority

    def validate_priority_order(
        priority: PriorityPatch,
    ) -> PriorityPatch:
        if priority.order is not None:
            if priority.order <= 0:
                raise ValueError("Order must be greater than 0")
            return priority

    def validate_priority(priority: PriorityPatch) -> PriorityPatch:
        try:
            PriorityPatchValidator.validate_priority_name(priority)
            PriorityPatchValidator.validate_priority_color(priority)
            PriorityPatchValidator.validate_priority_icon(priority)
            PriorityPatchValidator.validate_priority_order(priority)
            return priority
        except ValueError as e:
            raise ValidationError(custom_message=str(e))

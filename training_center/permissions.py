from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrTeacherLimitedEdit(BasePermission):
    """
    Admin: to‘liq CRUD
    Teacher: faqat PUT/PATCH (title o‘zgartirish)
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_admin or user.is_teacher)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin: to‘liq ruxsat
        if user.is_admin:
            return True

        # Teacher: faqat PATCH va faqat 'title' ni o‘zgartirsa bo‘ladi
        if user.is_teacher and request.method in ['PATCH', 'PUT', 'GET']:
            allowed_fields = {'title'}
            incoming_fields = set(request.data.keys())
            return incoming_fields.issubset(allowed_fields)

        return False


class IsStaffOrReadOnly(BasePermission):
    """
    Faqat is_staff foydalanuvchilar uchun CRUD ruxsat.
    Boshqa foydalanuvchilar faqat o'qiy olishadi.
    """

    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS ruxsat etilgan (read only)
        if request.method in SAFE_METHODS:
            return True
        # create, update, delete uchun faqat is_staff foydalanuvchilarga ruxsat
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'user')  # ya'ni Teacher borligini tekshiradi


# Staff bo‘lsa, CRUD qilish huquqini beramiz.
class IsStaffUser(BasePermission):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated and request.user.is_staff)

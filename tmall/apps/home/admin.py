import xadmin
from xadmin import views

# 主题的修改



class BaseSystemSettings:
    # 开启修改主题
    enable_themes = True
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSystemSettings)


class GlobalSettings:
    site_title = '后台'
    site_footer = '飘哥'


xadmin.site.register(views.CommAdminView, GlobalSettings)


class TestAdmin:
    # 后台管理界面显示的列
    list_display = ['tid', 'name']
    # 搜索的列名
    search_fields = ['name']
    # 分页显示的条数
    list_per_page = 10
    # -tid是逆序
    ordering = ['tid']
    # 不允许编辑
    readonly_fields = ['name']





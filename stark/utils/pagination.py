"""
分页组件
"""


class Paginator(object):
    def __init__(self, current_page, total_count, base_url, query_params, per_page_count=20, max_page_displayed=11):
        """__init__.

        :param self:
        :param current_page: 当前页码
        :param total_count: 数据库中数据的总条数
        :param base_url: 基础url
        :param query_params: QueryDict对象，包含当前url的原始查询条件
        :param per_page_count: 每页最多显示的数据条数
        :param max_page_displayed: 页面上最多显示的页码数量
        """
        try:
            self.current_page = int(current_page)
            if self.current_page <= 0:
                raise Exception()
        except Exception as e:
            self.current_page = 1
        self.total_count = total_count
        self.base_url = base_url
        self.query_params = query_params
        self.per_page_count = per_page_count
        self.max_page_displayed = max_page_displayed

        total_page_count, remainder = divmod(total_count, per_page_count)
        if remainder != 0:
            total_page_count += 1
        self.total_page_count = total_page_count

        half_page_count = int(max_page_displayed/2)
        self.half_page_count = half_page_count

    @property
    def start(self):
        """start.
        每页的起始索引, 用于给数据切片
        :param self:
        """
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        """end.
        每页的终止索引, 用于给数据切片
        :param self:
        """
        return self.current_page * self.per_page_count

    def page_html(self):
        """page_html.
        生成分页器的html代码
        情况1: 显示页数为3, 总页数为2:
           分页逻辑                页面显示
        1*·2                上一页 1· 2 下一页
        1* 2·               上一页 1  2· 下一页
        情况2: 显示页数为3，总页数为5:
           分页逻辑                页面显示
        1*·2  3# 4  5       上一页 1· 2  3  下一页
        1* 2· 3# 4  5       上一页 1  2· 3  下一页
        1  2* 3· 4# 5       上一页 2  3· 4  下一页
        1* 2  3* 4· 5#      上一页 3  4· 5  下一页
        1  2  3* 4  5·#     上一页 3  4  5·#下一页
            *: 起始页
            ·: 当前页
            #: 终止页
        """
        if self.total_page_count <= self.max_page_displayed:
            start_page = 1
            end_page = self.total_page_count
        elif self.current_page + self.half_page_count <= self.max_page_displayed:

            start_page = 1
            end_page = self.max_page_displayed
        elif self.current_page + self.half_page_count <= self.total_page_count:
            start_page = self.current_page - self.half_page_count + 1
            end_page = self.current_page + self.half_page_count
        else:
            start_page = self.total_page_count - self.max_page_displayed
            end_page = self.total_page_count

        page_list = []
        # 上一页
        if self.current_page <= 1:
            prev = "<li><a href='#'>上一页</a></li>"
        else:
            self.query_params["page"] = self.current_page - 1
            prev = "<li><a href='%s?%s'>上一页</a></li>" % (
                self.base_url, self.query_params.urlencode())
        page_list.append(prev)

        # 数字页
        for i in range(start_page, end_page + 1):
            self.query_params["page"] = i
            if self.current_page == i:
                numbe = "<li class='active'><a href='%s?%s'>%s</a></li>" % (
                    self.base_url, self.query_params.urlencode(), i)
            else:
                numbe = "<li><a href='%s?%s'>%s</a></li>" % (
                    self.base_url, self.query_params.urlencode(), i)
            page_list.append(numbe)

        # 下一页
        if self.current_page >= self.total_page_count:
            nex = "<li><a href='#'>下一页</a></li>"
        else:
            self.query_params["page"] = self.current_page + 1
            nex = "<li><a href='%s?%s'>下一页</a></li>" % (
                self.base_url, self.query_params.urlencode())
        page_list.append(nex)

        page_str = "".join(page_list)
        return page_str

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import datetime
from geojson import Polygon
import datetime


class sentinel_query_task:
    user = 'tranvandung20121439'
    password = 'dung20121439'
    api_url = 'https://scihub.copernicus.eu/dhus'
    api = SentinelAPI(user, password, api_url)

    def query(self, platformname, min_lon, max_lon, min_lat, max_lat, start_time, end_time):
        def order_by(order_by='ingestiondate', ascending=False):
            prefix_order_by = '+' if ascending else '-'
            order_by = prefix_order_by + order_by
            return order_by

        min_lon, max_lon, min_lat, max_lat = self.validate_coord(min_lon), self.validate_coord(max_lon), self.validate_coord(min_lat), self.validate_coord(max_lat)
        extent = Polygon([[(min_lon, max_lat),
                           (max_lon, max_lat),
                           (max_lon, min_lat),
                           (min_lon, min_lat),
                           (min_lon, max_lat)]])
        extent = geojson_to_wkt(extent)

        start_time, end_time = self.validate_date(start_time), self.validate_date(end_time)

        order_by = order_by('ingestiondate', ascending=False)
        products = self.api.query(extent,
                             date=(start_time, end_time),
                             area_relation='Intersects',
                             cloudcoverpercentage=(0, 10),
                             platformname=platformname,
                            order_by=order_by
                                ) #producttype='S2MSI2A'
        self.products = products
        products_df = self.api.to_dataframe(products)
        self.products_df = products_df
        return self.products_df

    def validate_date(self, date):
        if type(date) is str:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        return date

    def validate_coord(self, x):
        return float(x)

    def download(self, uuid, directory_path='.'):
        self.api.download(uuid, directory_path)

    def get_title_by_uuid(self, uuid):
        product_odata = self.api.get_product_odata(uuid)
        return product_odata['title']
import traceback
import pymysql
from datetime import datetime, timedelta


def write_to_file(file_name, data):
    with open(file_name, 'w') as f:
        for _string in data:
            # f.seek(0)
            f.write(str(_string) + '\n')

        f.close()


def gen_rfield_d03(model, version):
    # Connect to the database
    connection = pymysql.connect(host='35.230.102.148',
            user='root',
            password='cfcwm07',
            db='curw_fcst',
            cursorclass=pymysql.cursors.DictCursor)

    start_time = ''
    end_time = ''

    now = datetime.strptime((datetime.now()+timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S')

    try:

        # Extract timeseries start time and end time
        with connection.cursor() as cursor1:
            cursor1.callproc('get_TS_start_end', (model, version))
            result = cursor1.fetchone()
            start_time = result.get('start')
            end_time = result.get('end')

        # Extract rfields
        timestamp = start_time
        while timestamp <= end_time :
            # rfield = [['latitude', 'longitude', 'rainfall']]
            rfield = []
            with connection.cursor() as cursor2:
                cursor2.callproc('get_d03_rfield', (model, version, timestamp))
                results = cursor2.fetchall()
                for result in results:
                    rfield.append('{} {} {}'.format(result.get('longitude'), result.get('latitude'), result.get('value')))

            if timestamp < now:
                write_to_file('/var/www/html/wrf/{}/rfield/d03/past/{}_{}_{}_rfield.txt'.format(version, model, version, timestamp), rfield)
            else:
                write_to_file('/var/www/html/wrf/{}/rfield/d03/future/{}_{}_{}_rfield.txt'.format(version, model, version, timestamp), rfield)

            timestamp = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S') + timedelta(minutes=15)

    except Exception as ex:
        traceback.print_exc()
    finally:
        connection.close()
        print("Process finished")


gen_rfield_d03("WRF_A", "v4")
gen_rfield_d03("WRF_C", "v4")
gen_rfield_d03("WRF_E", "v4")
gen_rfield_d03("WRF_SE", "v4")
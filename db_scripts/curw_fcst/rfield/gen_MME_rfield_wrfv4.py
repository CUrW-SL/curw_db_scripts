import traceback
import pymysql
from datetime import datetime, timedelta


def average_timeseries(timeseries):
    """
    Give the timeseries with avg of 2 model values
    :param timeseries: input timeseries e.g. list of lists like [longitude, latitude, model1_value, model2_value]
    :return: list of lists like [longitude, latitude, avg_value]
    """
    avg_timeseries = []

    for i in range(len(timeseries)):
        # print("############", timeseries[i][2], timeseries[i][3], timeseries[i][2]+timeseries[i][3])
        avg_timeseries.append([timeseries[i][0], timeseries[i][1], '%.3f' % ((timeseries[i][2]+timeseries[i][3])/2)])

    # for i in range(len(timeseries)):
    #     print("*****", avg_timeseries[i])

    return avg_timeseries


def write_to_file_list_of_lists(file_name, data):
    with open(file_name, 'w') as f:
        for _list in data:
            for i in range(len(_list) - 1):
                # f.seek(0)
                f.write(str(_list[i]) + ' ')
            f.write(str(_list[len(_list) - 1]))
            f.write('\n')

        f.close()


def gen_MME_rfield_d03_kelani_basin(model1, version1, model2, version2):

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
            cursor1.callproc('get_TS_start_end', (model1, version1))
            # parameters are given to above procedure assuming all data of models in model_list are included in
            # one netcdf file and have same start, end timestamps
            result = cursor1.fetchone()
            start_time = result.get('start')
            end_time = result.get('end')

        # Extract rfields
        timestamp = start_time
        while timestamp <= end_time :
            # rfield = [['latitude', 'longitude', 'rainfall']]
            rfield = []

            temp_rfield = []

            print_line = []

            with connection.cursor() as cursor2:
                cursor2.callproc('get_d03_rfield_kelani_basin_rainfall', (model1, version1, timestamp))
                results = cursor2.fetchall()
                for result in results:
                    temp_rfield.append([result.get('longitude'), result.get('latitude'), result.get('value')])
                    print_line.append([result.get('longitude'), result.get('latitude')])

            with connection.cursor() as cursor3:
                cursor3.callproc('get_d03_rfield_kelani_basin_rainfall', (model2, version2, timestamp))
                results = cursor3.fetchall()
                count = 0
                for result in results:
                    # this value is appended assuming all output generated by the procedure call (sorts according to
                    # the lon lat) are in same order
                    temp_rfield[count].append(result.get('value'))
                    print_line[count].append([result.get('longitude'), result.get('latitude')])
                    count += 1

            rfield = average_timeseries(temp_rfield)

            for i in range(len(rfield)):
                print(print_line[i])
                print(temp_rfield[i][2], temp_rfield[i][3], rfield[i][2])

            # if timestamp < now:
            #     write_to_file_list_of_lists('/var/www/html/wrf/v4/rfield/kelani_basin/past/WRF_MME_v4_{}_rfield.txt'
            #         .format(timestamp), rfield)
            # else:
            #     write_to_file_list_of_lists('/var/www/html/wrf/v4/rfield/kelani_basin/future/WRF_MME_v4_{}_rfield.txt'
            #         .format(timestamp), rfield)

            timestamp = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S') + timedelta(minutes=15)

    except Exception as ex:
        traceback.print_exc()
    finally:
        connection.close()
        print("Process finished")


# gen_MME_rfield_d03_kelani_basin(model1="WRF_E", version1="v4", model2="WRF_SE", version2="v4")


timeseries = [["lon", "lat", 2, 2], ["lon", "lat", 3, 2], ["lon", "lat", 4, 4]]

print(average_timeseries(timeseries))
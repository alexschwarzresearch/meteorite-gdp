import csv
import os

import plotly.graph_objs as go
import plotly.offline as offline
import pycountry
import reverse_geocoder as rg

DATASET_PATH_METEORITES = '../res/Meteorite-Landings.csv'
DATASET_PATH_GDP = '../res/gdp_csv.csv'
YEAR = "2016"

OUTPUT_FILE_CSV = '../out/meteors_gdp.csv'
OUTPUT_FILE_TEMP_HTML = '../out/temp.html'


def get_meteorite_mass_list():
    mass_list = []
    geocode_list = []
    country_list = []

    with open(DATASET_PATH_METEORITES, 'r', encoding='utf8') as f:
        reader = csv.reader(f)

        # skip header
        next(reader)

        for row in reader:
            if not ("NotAvailable" in row[4] or "NotAvailable" in row[7]):
                mass = float(row[4][9:row[4].index(',')])
                mass_list.append(mass)

                lat = float(row[7][13:row[7].index(',')])
                lon = float(row[7][row[7].index(',') + 2:-2])
                geocode_list.append((lat, lon))

    geocode_list = rg.search(geocode_list)

    # convert ISO 2 letter country code to 3 letter code
    for elem in geocode_list:
        country_list.append(pycountry.countries.get(alpha_2=elem.get('cc')).alpha_3)

    mass_country_list = list(zip(mass_list, country_list))

    # group mass for each country
    grouped_country_dict = dict()
    for elem in mass_country_list:
        if elem[1] in grouped_country_dict:
            grouped_country_dict[elem[1]] = grouped_country_dict[elem[1]] + elem[0]
        else:
            grouped_country_dict[elem[1]] = elem[0]

    sorted_mass_per_country = sorted(grouped_country_dict.items(), key=lambda x: x[1])
    return sorted_mass_per_country


def get_gdp_dict():
    gdp_dict = dict()

    with open(DATASET_PATH_GDP, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            if row[2] == YEAR:
                gdp_dict[row[1]] = float(row[3])

    return gdp_dict


def write_result(countries, meteors, gdp):
    # create directory if it not exists
    os.makedirs(os.path.dirname(OUTPUT_FILE_CSV), exist_ok=True)

    with open(OUTPUT_FILE_CSV, 'w', newline='') as out:
        writer = csv.writer(out, delimiter=',')
        writer.writerow(['Country', 'Meteor Mass', 'GDP'])

        for c, m, g in zip(countries, meteors, gdp):
            writer.writerow([c, m, g])


def plot_result(countries, meteors, gdp):
    trace_meteors = go.Scatter(
        x=countries,
        y=meteors,
        name='Meteor Mass',
        line=dict(
            color='rgb(205, 12, 24)',
            width=4
        )
    )
    trace_gdp = go.Scatter(
        x=countries,
        y=gdp,
        name='GDP',
        line=dict(
            color='rgb(22, 96, 167)',
            width=4
        ),
        yaxis='y2'
    )

    layout = go.Layout(
        title='Mass of Meteors and GDP of Countries',
        titlefont=dict(size=35),

        legend=dict(
            font=dict(size=20),
            x=0.1,
            y=0.9
        ),

        yaxis=dict(
            title='mass in kg',
            range=[0, 150_000]
        ),
        yaxis2=dict(
            title='USD',
            overlaying='y',
            side='right',
            range=[0, 20_000_000_000_000]
        )
    )

    fig = dict(data=[trace_meteors, trace_gdp], layout=layout)

    offline.init_notebook_mode()
    offline.plot(
        fig,
        image='png',
        filename=OUTPUT_FILE_TEMP_HTML,
        image_filename="meteors_gdp",
        image_width=1500,
        image_height=930
    )


def main():
    # get 20 countries with the largest mass of meteorites
    meteorite_mass_list = get_meteorite_mass_list()[-20:]

    gdp_dict = get_gdp_dict()

    combined_list = []
    for elem in meteorite_mass_list:
        if elem[0] in gdp_dict:
            combined_list.append((elem[0], elem[1], gdp_dict.get(elem[0])))

    countries = [pycountry.countries.get(alpha_3=x[0]).name for x in combined_list]

    # truncate long names
    countries = list(map(lambda x: x if ',' not in x else x[:x.index(',')], countries))

    # convert mass to kg and round to 4 decimal places
    meteors = [round((x[1] / 1000.0), 4) for x in combined_list]

    gdp = [x[2] for x in combined_list]

    write_result(countries, meteors, gdp)
    plot_result(countries, meteors, gdp)


if __name__ == '__main__':
    main()

from lineage_platform.parsers.qlikview.qvs_parser import (
    QVSParser
)


def test_synthetic_fields():

    parser = QVSParser()

    app = parser.parse(
        'data/input/qlikview/08_realistic_dashboard.qvs'
    )

    field_names = [

        field.name

        for field in app.fields
    ]

    assert 'AmountWithTax' in field_names

    assert 'CustomerStatus' in field_names

    assert 'OrderCount' in field_names
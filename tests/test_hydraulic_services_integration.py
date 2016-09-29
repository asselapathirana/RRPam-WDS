from rrpam_wds import hydraulic_services as hs

def test_standard_example_Net_3_of_epanettools_give_correct_total_demand():
    import os
    from epanettools.examples import simple 
    file = os.path.join(os.path.dirname(simple.__file__),'Net3.inp')
    pd=hs.pdd_service(file)
    assert abs(pd.get_total_demand()-6.91)<.1
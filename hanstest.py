import resources.lib.hanssettings

h = resources.lib.hanssettings.HansSettings()

print(h)

if (h):
    #print(h.get_overzicht(h.get_dataoverzicht()))
    print('\n\n')
    filedata = h.get_data_from_github_file('userbouquet.stream_muziek.tv')
    #filedata = h.get_datafromfilegithub('userbouquet.stream_nl_nationaal.tv')
    #print(h.get_name(filedata,'userbouquet.stream_nl_nationaal.tv'))
    #print(h.get_items(filedata))
    print(h.get_items_subfolder(filedata, '1'))

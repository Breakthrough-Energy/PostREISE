from matplotlib import pyplot as plt

def carbon_barchart(dict1, dict2, name1, name2):
    plt.rcParams.update({'font.size': 22})
    fig = plt.figure(figsize=(7,2))
    objects = ( name1, name2)
    y_pos = np.arange(len(objects))
    carbon_val = [sum(dict1['coal'].values()),
               sum(dict2['coal'].values())]

    plt.barh(y_pos, carbon_val, align='center', alpha=0.25, color = ['black'])

    plt.yticks(y_pos, objects)
    plt.xticks(np.arange(0, 2.1e8, .5e8))
    plt.xlabel('Tons')
    plt.title('Coal: C$O_2$  Emissions', y=1.04)
    #plt.tight_layout()

    plt.show()

    fig = plt.figure(figsize=(7,2))
    objects = ('2030 all match CA', '2016 base')
    y_pos = np.arange(len(objects))
    carbon_val = [sum(dict1['ng'].values()),
               sum(dict2['ng'].values())]

    plt.barh(y_pos, carbon_val, align='center', alpha=0.25, color = ['purple'])

    plt.yticks(y_pos, objects)
    plt.xticks(np.arange(0, 2.1e8, .5e8))
    plt.xlabel('Tons')
    plt.title('Natural Gas: C$O_2$ Emissions', y=1.04)
    #plt.tight_layout()

    plt.show()
    return
    
def carbon_percentdiff(dict1, dict2):
    sum1 = sum(dict1['coal'].values()) + sum(dict1['ng'].values())
    sum2 = sum(dict2['coal'].values()) + sum(dict2['ng'].values())
    print(round(100*(1- sum2/sum1),2))
    return
let chartInstances = {};
let detailKey;
let detailHistoryData = {};

function updateCharts() {
    fetch('/cloud/metrics/api?key=__all__')
        .then(response => response.json())
        .then(data => {
            updateServiceData(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function updateServiceData(newData) {
    if (Object.keys(chartInstances).length === 0) {
        createInitialCharts(newData);
    }
    updateExistingCharts(newData);
}

function createInitialCharts(data) {
    const serviceGrid = document.getElementById('serviceGrid');
    serviceGrid.innerHTML = '';

    Object.keys(data).forEach(serviceName => {
        const service = data[serviceName];
        const serviceCard = document.createElement('div');
        serviceCard.className = 'service-card';
        serviceCard.id = 'serviceCard_' + serviceName;
        serviceCard.innerHTML = `
                <div class="service-header">
                    <div class="service-name" onclick="handleServiceNameClick('${serviceName}')">${serviceName}</div>
                    <div class="service-status ${service.status === 'up' ? 'status-up' : 'status-down'}">
                        ${service.status === 'up' ? 'Running' : 'Stopped'}
                    </div>
                `;
        serviceGrid.appendChild(serviceCard);

        chartInstances[serviceName] = {
            status: serviceCard.querySelector('.service-status'),
        };
    });
}

function handleServiceNameClick(serviceName) {
    detailKey = serviceName;
    if (!detailHistoryData[detailKey]) {
        detailHistoryData[detailKey] = {};
    }
    const detailTab = document.querySelector('.tab[data-tab="detail"]');
    detailTab.click();
}

function initChart(title, data_list, serviceName, datetime) {
    if (!data_list || data_list.length === 0) {
        return null;
    }

    let unit = '';
    const color = getServiceColor(serviceName)

    let series = [];
    Object.keys(data_list).forEach(attr => {
        unit = data_list[attr].unit;
        const value = data_list[attr].value;
        series.push({
            name: attr,
            data: [value],
            type: 'line',
            smooth: true,
            areaStyle: {
                color: color
            },
            lineStyle: {
                color: color
            },
            itemStyle: {
                color: color
            }
        })
    })

    const serviceCard = document.getElementById('serviceCard_' + serviceName);
    const chartContainer = document.createElement('div');
    chartContainer.className = "chart-container";
    serviceCard.appendChild(chartContainer);

    const chart = echarts.init(chartContainer);

    const option = {
        title: {
            text: title,
            textStyle: {color: '#fff'}
        },
        tooltip: {
            trigger: 'item',
            formatter: function (item) {
                return `${item.seriesName}: ${item.value.toFixed(2)}${unit}`
            }
        },
        legend: {
            data: [serviceName],
            textStyle: {color: '#fff'}
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: [datetime],
            axisLabel: {
                color: '#fff',
                formatter: function (value) {
                    return value;
                }
            }
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                color: '#fff',
                formatter: function (value) {
                    return `${value}${unit}`;
                }
            },
        },
        series: series,
    };
    chart.setOption(option);
    return chart;
}

function getServiceColor(serviceName) {
    const colors = [
        '#5470c6',
        '#91cc75',
        '#fac858',
        '#ee6666',
        '#73c0de',
        '#3ba272',
        '#fc8452',
        '#9a60b4',
        '#ea7ccc'
    ];
    let hash = 0;
    for (let i = 0; i < serviceName.length; i++) {
        hash = serviceName.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}

function updateExistingCharts(newData) {
    Object.keys(newData).forEach(serviceName => {
        const service = newData[serviceName];
        const charts = chartInstances[serviceName];

        const statusElement = charts.status;
        statusElement.className = `service-status ${service.status === 'up' ? 'status-up' : 'status-down'}`;
        statusElement.textContent = service.status === 'up' ? 'Running' : 'Stopped';
        delete service.status;

        if (!service.values) {
            return;
        }

        // CPU, Memory, Network
        updateChart(charts, 'cpu', service.values.cpu, serviceName, service.time);
        updateChart(charts, 'memory', service.values.memory, serviceName, service.time);
        updateChart(charts, 'network', service.values.network, serviceName, service.time);
        delete service.values.cpu
        delete service.values.memory
        delete service.values.network

        // Extra
        Object.keys(service.values).forEach(name => {
            updateChart(charts, name, service[name], serviceName, service.time);
        })
    })
}

function updateChart(charts, title, newData_list, serviceName, datetime) {
    if (!newData_list) {
        return;
    }

    if (!charts[title]) {
        charts[title] = initChart(title, newData_list, serviceName, datetime)
        return;
    }

    const chart = charts[title];

    const option = chart.getOption();

    const currentTimestamps = option.xAxis[0].data;

    if (currentTimestamps.length > 0 && currentTimestamps[currentTimestamps.length - 1] === datetime) {
        return;
    }

    const updatedTimestamps = [...currentTimestamps, ...datetime];
    if (updatedTimestamps.length > 10) {
        const removeCount = updatedTimestamps.length - 10;
        updatedTimestamps.splice(0, removeCount);
    }
    option.xAxis[0].data = updatedTimestamps;

    const valueSeries = {}
    option.series.forEach(v => {
        valueSeries[v.name] = v;
    })

    const series = [];
    Object.keys(newData_list).forEach(attr => {
        const updatedSeries = [...valueSeries[attr].data, newData_list[attr].value];
        if (updatedSeries.length > 100) {
            const removeCount = updatedSeries.length - 100;
            updatedSeries.splice(0, removeCount);
        }
        valueSeries[attr].data = updatedSeries;
        series.push(valueSeries[attr]);
    })

    const axisLabel = {
        color: '#fff',
        formatter: function (value, index) {
            if (index === 0 || index === updatedTimestamps.length - 1) {
                return value
            }
            return ''
        }
    }

    chart.setOption({
        xAxis: {
            data: updatedTimestamps,
            axisLabel: axisLabel
        },
        yAxis: {
            color: '#fff',
            formatter: function (value) {
                return `${value}`;
            },
            // max: value_max
        },
        series: series,
    });
}

function updateDetailCharts() {
    if (detailKey === undefined) {
        return;
    }

    fetch('/cloud/metrics/api?key=' + detailKey)
        .then(response => response.json())
        .then(data => {
            updateDetailData(data.values);
        })
        .catch(error => console.error('Error fetching detail data:', error));
}

function updateDetailData(data) {
    const keyTitle = {
        "cpu": "CPU",
        "memory": "Memory",
        "network": "Network",
    }
    const keys = ["cpu", "memory", "network"]
    keys.forEach(key => {
        if (Object.hasOwn(data, key)) {
            updateDetailChart(keyTitle[key], key, data[key])
            delete data[key]
        }
    })

    Object.keys(data).forEach(name => {
        updateDetailChart(name, name, data[name]);
    })
}

function updateDetailAttributeChart(title, name, data) {
    let element = document.getElementById(name + 'DetailChart');
    if (!element) {
        element = document.createElement('div');
        element.className = 'detail-chart';
        element.id = name + 'DetailChart';
        document.getElementById('detail').appendChild(element);
    }

    const detailChart = echarts.init(element);
    const xAxisData = [];
    const series = [];
    if (!detailHistoryData[detailKey][name]) {
        detailHistoryData[detailKey][name] = {};
    }
    let dataHistory = detailHistoryData[detailKey][name];

    let value_max;
    let unit = '';

    Object.keys(data).forEach((id) => {
        const serviceData = data[id];
        const timestamps = serviceData.time;
        const values = serviceData.value;

        if (!serviceData.unit || serviceData.unit.lenght === 0) {
            return;
        }

        unit = serviceData.unit[0];
        if (unit === '%') {
            value_max = 100;
        }

        if (!dataHistory[id]) {
            dataHistory[id] = {
                timestamps: [],
                values: []
            };
        }

        dataHistory[id].timestamps = dataHistory[id].timestamps.concat(timestamps);
        dataHistory[id].values = dataHistory[id].values.concat(values);
        if (dataHistory[id].timestamps.length > 100) {
            const removeCount = dataHistory[id].timestamps.length - 100;
            dataHistory[id].timestamps.splice(0, removeCount);
            dataHistory[id].values.splice(0, removeCount);
        }

        dataHistory[id].timestamps.forEach((timestamp) => {
            if (!xAxisData.includes(timestamp)) {
                xAxisData.push(timestamp);
            }
        });

        series.push({
            name: `${id}`,
            data: dataHistory[id].values,
            type: 'line',
            smooth: true,
            areaStyle: {}
        });
    });

    xAxisData.sort();

    const option = {
        title: {
            text: title,
            textStyle: {color: '#fff'}
        },
        tooltip: {
            trigger: 'item',
            formatter: function (item) {
                return `${item.seriesName}: ${item.value.toFixed(2)}${unit}`
            }
        },
        legend: {
            data: Object.keys(data).map((id) => `${id}`),
            textStyle: {color: '#fff'}
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: xAxisData,
            axisLabel: {
                color: '#fff',
                formatter: function (value) {
                    return value;
                }
            }
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                color: '#fff',
                formatter: function (value) {
                    return `${value}${unit}`;
                }
            },
            max: value_max
        },
        series: series
    };

    detailChart.setOption(option);
}

function updateDetailChart(title, name, data) {
    Object.keys(data).forEach(attr => {
        updateDetailAttributeChart(`${title} ${attr} Detail`, `${name}_${attr}`, data[attr]);
    })
}

function windowOnLoad() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.remove('hidden');

            if (tab.dataset.tab === 'detail') {
                tab.innerHTML = detailKey + ' Monitoring';
                updateDetailCharts();
            }
        });
    });

    updateCharts()

    setInterval(() => {
        if (!document.getElementById('overview').classList.contains('hidden')) {
            updateCharts();
        } else {
            updateDetailCharts();
        }
    }, 10 * 1000);
}

window.addEventListener('load', windowOnLoad);

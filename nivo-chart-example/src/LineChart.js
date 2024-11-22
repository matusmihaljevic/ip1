import { ResponsiveLine } from '@nivo/line';
import { useEffect, useState } from 'react';


// Funkcia na generovanie náhodnej hodnoty
function nextRandomVal(prev, limit, maxStep = 5) {
    const modifier = Math.round(Math.random() * maxStep * 2 - maxStep);
    let next = prev + modifier;
    if (next > limit) {
      next = limit - maxStep;
    } else if (next < 0) {
      next = maxStep;
    }
    return next;
  }
  
  // Funkcia na generovanie dát
  function generateRuleData(historyLength, interval) {
    const now = new Date().getTime();
    const data = [];
    let packets_in = 50000000;
    let packets_out = 60000000;
  
    for (let time = now - historyLength; time <= now; time += interval) {
      packets_in = nextRandomVal(packets_in, 148000000, 1000000);
      packets_out = packets_in + nextRandomVal(20000000, 500000000, 2000000);
      data.push({
        time_start: new Date(time),  // Používame Date objekt pre čas
        packets_in,
        packets_out,
      });
    }
    return data;
  }
  
  const LineChart = () => {
    const [chartData, setChartData] = useState(() => generateRuleData(10000 * 1000, 1000));

    // Function to update the chart with new data
    const updateChartData = () => {
        const lastData = chartData[chartData.length - 1];
        const lastTime = new Date(lastData.time_start).getTime();
        
        let packets_in = lastData.packets_in;
        let packets_out = lastData.packets_out;

        const newData = [];
        for (let i = 0; i < 60; i++) { // Adjust the number of new data points as needed
            const time = lastTime + (i + 1) * 1000; // Increment by 1 second
            packets_in = nextRandomVal(packets_in, 148000000, 1000000);
            packets_out = packets_in + nextRandomVal(20000000, 500000000, 2000000);
            newData.push({
                time_start: new Date(time),  // Use Date object for x
                packets_in,
                packets_out,
            });
        }

        // Update the chart data state
        setChartData((prevData) => [...prevData, ...newData]);
    };

    // Update the chart every second using setInterval
    useEffect(() => {
        const intervalId = setInterval(updateChartData, 1000); // 1 second interval

        return () => clearInterval(intervalId); // Cleanup on component unmount
    }, [chartData]);

    const formattedData = [
        {
            id: 'Packets In',
            data: chartData.map(item => ({
                x: item.time_start,  // Use Date object for x-axis
                y: item.packets_in,
            })),
        },
        {
            id: 'Packets Out',
            data: chartData.map(item => ({
                x: item.time_start,  // Use Date object for x-axis
                y: item.packets_out,
            })),
        },
    ];  

    return (
        <div style={{ height: '300px' }}>
            <ResponsiveLine
            data={formattedData}
            xScale={{ type: 'time', format: 'native' }}
            xFormat="time:%Y-%m-%d %H:%M:%S"
            yScale={{ type: 'linear' }}
            axisBottom={{
                format: '%H:%M:%S',
                legend: 'Time',
                legendPosition: 'middle',
                legendOffset: 32,
            }}
            axisLeft={{
                legend: 'Packets',
                legendPosition: 'middle',
                legendOffset: -40,
            }}
            margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
            useMesh={false}
            enableArea={true}
            motionConfig="none"
            lineWidth={1}
            enablePoints={false}
            />
        </div>
    );    
  };
  
  export default LineChart;
  
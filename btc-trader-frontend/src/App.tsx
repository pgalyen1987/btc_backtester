import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const WS_URL = 'ws://localhost:5000/data';

interface HistoricalData {
  timestamp: string;
  price: number;
  volume: number;
}

interface MarketData {
  price: number;
  volume: number;
  high: number;
  low: number;
}

interface WebSocketData {
  type: string;
  historical: HistoricalData[];
  current: MarketData;
}

export default function App() {
  const [data, setData] = useState<WebSocketData | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    
    ws.onmessage = (event) => {
      try {
        const wsData = JSON.parse(event.data);
        if (wsData.type === 'data_update') {
          setData(wsData);
        }
      } catch (error) {
        console.error('Error parsing websocket data:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.close();
    };
  }, []);

  if (!data) {
    return <div>Loading data...</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>BTC Price History</h1>
      
      {/* Price Chart */}
      <div style={{ marginTop: '20px' }}>
        <h2>Price History (24h)</h2>
        <LineChart width={800} height={400} data={data.historical}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(value) => new Date(value).toLocaleTimeString()}
          />
          <YAxis domain={['auto', 'auto']} />
          <Tooltip 
            labelFormatter={(value) => new Date(value).toLocaleString()}
            formatter={(value: any) => ['$' + value.toLocaleString(), 'Price']}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#8884d8" 
            name="BTC Price"
            dot={false}
          />
        </LineChart>
      </div>

      {/* Current Market Data */}
      <div style={{ marginTop: '20px' }}>
        <h2>Current Market</h2>
        <div>
          <p>Price: ${data.current.price.toLocaleString()}</p>
          <p>Volume: {data.current.volume.toLocaleString()} BTC</p>
          <p>24h High: ${data.current.high.toLocaleString()}</p>
          <p>24h Low: ${data.current.low.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}

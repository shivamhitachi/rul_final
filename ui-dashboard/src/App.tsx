/**
 * @file      : App.tsx
 * @summary   :
 * @author    : Charles Best <cbest@nvidia.com>
 * @created   : 2023-12-14
 * @copywrite : 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * @exports   : App
 */

import './App.css';
import React, { useEffect, useState } from 'react';
import mqtt from 'mqtt';
import Window from './Window';

function App() {
  const [mqttClient, setMqttClient] = useState<any>(null);

  useEffect(() => {
    // The user is already authenticated, so we can connect to MQTT directly.
    const client = mqtt.connect('ws://localhost:9001');

    client.on('connect', () => {
      console.log('Connected to MQTT broker');
      client.publish('RUL/startup', 'TRUE');
    });

    client.on('error', (err) => {
      console.error('MQTT error:', err);
    });

    setMqttClient(client);

    // Cleanup function to close the connection when the component unmounts.
    return () => {
      if (client && client.connected) {
        console.log('Disconnecting MQTT client');
        client.end();
      }
    };
  }, []); // Empty dependency array means this runs once when App mounts.

  // No need for an isAuthenticated check here anymore.
  // If the App renders, we are authenticated.
  return <Window />;
}

export default App;
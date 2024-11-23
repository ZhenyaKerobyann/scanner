import React, { useState, useEffect, useRef } from "react";
import Hero from "./components/hero";
import Scanner from "./components/scanner";
import Console from "./components/console";

function App() {
  const [logs, setLogs] = useState([]);
  const ws = useRef(null);

  const onStartScan = (url, option) => {
    fetch(`http://127.0.0.1:8000/logs/scan/${option.value}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        url,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Display the JSON response in a formatted way
        console.log(JSON.stringify(data, null, 4));
      })
      .catch((error) => {
        console.log("An error occurred: " + error);
      });
    setLogs([]);

    if (ws.current) {
      return;
    }

    ws.current = new WebSocket("ws://127.0.0.1:8000/ws/logs/");

    ws.current.onmessage = (e) => {
      console.log("data ----- ", e.data);
      const result = JSON.parse(e.data);
      setLogs((prevLogs) => [...prevLogs, {date: new Date().toLocaleTimeString(), message: result.message}]);
    };

    ws.current.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.current.onclose = () => {
      console.log("WebSocket connection closed");
    };
  };

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const downloadLogs = () => {
    const logStrings = logs.map((log) => `[${log.date}] ${log.message.replaceAll('~', '')}`);
    const file = new Blob([logStrings.join("\n")], { type: "text/plain" });
    const element = document.createElement("a");
    element.href = URL.createObjectURL(file);
    element.download = "logs.txt";
    document.body.appendChild(element); // For FireFox
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div>
      <Hero />
      <Scanner onStartScan={onStartScan} />
      <Console logs={logs} />
      <div className="flex justify-center bg-gray-100 py-10">
        <button
          className="rounded bg-blue-600 px-4 py-2 text-white transition duration-300"
          onClick={downloadLogs}
        >
          Download Logs
        </button>
      </div>
    </div>
  );
}

export default App;

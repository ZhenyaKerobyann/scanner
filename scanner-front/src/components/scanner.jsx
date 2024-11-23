import React, { useState } from "react";

const Options = {
  cors: {
    name: "Cors",
    value: "cors",
  },
  csrf: {
    name: "CSRF",
    value: "csrf",
  },
  sql_injection: {
    name: "SQL Injection",
    value: "sql_injection",
  },
  xss: {
    name: "XSS",
    value: "xss",
  },
};

function Scanner({ onStartScan }) {
  const [url, setUrl] = useState("");
  const [selectedOption, setSelectedOption] = useState(Options.cors);

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartScan(url, selectedOption);
  };

  return (
    <section id="scanner-section" className="bg-gray-100 py-20">
      <div className="container mx-auto text-center">
        <h2 className="text-3xl font-bold">
          Scan Your Website for Vulnerabilities
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-lg">
          Select the type of vulnerability you want to test for. Enter your
          website's URL and click "Start Scan" to identify potential security
          issues. Stay proactive and protect your web presence.
        </p>
        <div className="mt-8 flex justify-center space-x-4">
          {Object.keys(Options).map((option) => (
            <button
              key={option}
              className={`rounded px-4 py-2 transition duration-300 ${
                selectedOption.value === option
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
              onClick={() => setSelectedOption(Options[option])}
            >
              {Options[option]["name"]}
            </button>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="mt-8 flex justify-center">
          <input
            type="url"
            required
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-1/2 rounded-l border px-4 py-2 transition duration-300 focus:ring-0"
          />
          <button
            type="submit"
            className="rounded-r bg-gray-900 px-6 py-2 text-white transition duration-300 hover:bg-gray-700"
          >
            Start Scan
          </button>
        </form>
      </div>
    </section>
  );
}

export default Scanner;

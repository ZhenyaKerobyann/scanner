import React from "react";

export function TerminalModal({ isOpen, logs, toggleMaximize }) {
  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 transition-opacity duration-300 ${
        isOpen ? "opacity-100" : "pointer-events-none opacity-0"
      }`}
    >
      <div className="relative h-full w-full rounded-lg bg-white shadow-lg">
        <div className="flex h-full flex-col overflow-hidden rounded-md shadow-lg">
          <div className="flex items-center bg-gray-200 px-3 py-1.5">
            <div className="z-10 flex space-x-2">
              <button
                className="h-3 w-3 rounded-full bg-red-500"
                onClick={toggleMaximize}
              ></button>
              <button className="h-3 w-3 cursor-pointer rounded-full bg-yellow-500"></button>
              <button
                className="h-3 w-3 rounded-full bg-green-500"
                onClick={toggleMaximize}
              ></button>
            </div>
            <div className="-ml-7 flex-1 text-center text-sm text-gray-500">
              Terminal
            </div>
          </div>
          <div className="h-full overflow-y-auto bg-black p-4 font-mono text-sm text-green-400">
            {logs.length === 0 ? (
              <p className="text-gray-500">Waiting for logs...</p>
            ) : (
              logs.map((log, index) => (
                <p key={index}>
                  <span className="text-gray-500">
                    [{log.date}]
                  </span>{" "}
                  <span className={`${log.message.includes('~') ? 'text-red-400' : 'text-green-400'}`}>{log.message.replaceAll('~', '')}</span>
                </p>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

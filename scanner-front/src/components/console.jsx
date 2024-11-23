import React, { useState, useEffect } from "react";
import { TerminalModal } from "./terminal-modal";

function Console({ logs }) {
  const [isMaximized, setIsMaximized] = useState(false);

  // Toggle maximize state
  const toggleMaximize = () => {
    setIsMaximized((prev) => !prev);
  };

  useEffect(() => {
    if (isMaximized) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMaximized]);

  return (
    <>
      <div className="relative bg-gray-100 py-10 transition-all duration-500">
        <div className="mx-auto flex max-w-4xl flex-col overflow-hidden rounded-md shadow-lg">
          <div className="flex items-center bg-gray-200 px-3 py-1.5">
            <div className="z-10 flex space-x-2">
              <button className="h-3 w-3 cursor-pointer rounded-full bg-red-500"></button>
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
          <div className="h-80 overflow-y-auto bg-black p-4 font-mono text-sm">
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

      <TerminalModal
        isOpen={isMaximized}
        logs={logs}
        toggleMaximize={toggleMaximize}
      />
    </>
  );
}

export default Console;

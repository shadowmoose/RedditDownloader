import React, {useEffect} from 'react';
import {connectWS, disconnectWS, STATE} from "./app-util/app-state";
import {observer} from "mobx-react-lite";
import {configure} from "mobx";

configure({
    enforceActions: "never",
})

const App = () => {
    useEffect(() => {
        connectWS();

        return disconnectWS;
    }, []);

    return (
        <div className="app">
            <h1>I'm React running in Electron App!</h1>
            <StateDebug />
        </div>
    );
}


const StateDebug = observer(() => {
    return <div>
        <pre>
            {JSON.stringify(STATE, null, 4)}
        </pre>
    </div>
})
export default App;

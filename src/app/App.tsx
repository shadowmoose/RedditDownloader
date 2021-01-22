import { hot } from 'react-hot-loader';
import * as React from 'react';


const App = () => {
    console.log("Running App react code.");
    return <div>
        Running!
    </div>;
}

export default hot(module)(App);

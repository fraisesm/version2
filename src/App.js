import 'bootstrap/dist/css/bootstrap.min.css';
import NaviBar from './components/NaviBar';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
} from 'react-router-dom';

import {Home} from './Home';
import {Users} from './Users';
import {About} from './About';

function App() {
    return (
    <> 
    <Router>
    <NaviBar />
    <Routes>
    <Route path="/" element={<Home/>}/>
    <Route path="/Users" element={<Users/>}/>
    <Route path="/About" element={<About/>}/>
    </Routes>
    </Router>
    </>
);
}

export default App;
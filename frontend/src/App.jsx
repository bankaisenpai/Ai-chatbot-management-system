import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes/approutes";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;

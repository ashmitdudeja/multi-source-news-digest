import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DigestPage from './pages/DigestPage';
import TopicPage from './pages/TopicPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DigestPage />} />
          <Route path="/topic/:name" element={<TopicPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;

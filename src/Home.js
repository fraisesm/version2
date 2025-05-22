import React from 'react';
import TeamsTable from './TeamsTable'; 

export function Home() { // Именованный export
  return (
    <div className="container">
      <h1 className="ms-5">Следите в реальном времени за участниками конкурса:</h1>
      <TeamsTable />
    </div>
  );
}

export default Home; 

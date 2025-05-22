import { useState, useEffect } from 'react';
import { Table } from 'react-bootstrap';

function TeamsTable() {
  const [teams, setTeams] = useState([]);
  
  useEffect(() => {
    async function fetchTeams() {
      const response = await fetch('http://your-api-endpoint/teams');
      const data = await response.json();
      setTeams(data);
    }
    fetchTeams();
  }, []);

  return (
    <div className="mt-4">

      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Команда</th>
            <th>Статус</th>
            {[1,2,3,4,5,6].map(num => (
              <th key={num}>Файл {num}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {teams.map(team => (
            <tr key={team.id}>
              <td>{team.name}</td>
              <td className={team.status === 'подключена' ? 'text-success' : 'text-danger'}>
                {team.status}
              </td>
              {[1,2,3,4,5,6].map(num => (
                <td key={num}>{team[`file${num}`] || '-'}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

export default TeamsTable;
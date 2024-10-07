export default function App() {
  return (
    <>
      <h1 className="Title Board">Tic-tac-toe</h1>
      <Board />
    </>
  );
}

const Board = () => {
  return (
    <>
      <div className="board-row">
        <button className="Board-">X</button>
        <button className="Board-">X</button>
        <button className="Board-">X</button>
      </div>

      <div className="board-row">
        <button className="Board-">X</button>
        <button className="Board-">X</button>
        <button className="Board-">X</button>
      </div>

      <div className="board-row">
        <button className="Board-">X</button>
        <button className="Board-">X</button>
        <button className="Board-">X</button>
      </div>
    </>
  );
};

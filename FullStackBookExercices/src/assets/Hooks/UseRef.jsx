import { useRef } from "react";

export default function UseRefComponent() {
  const inputRef = useRef(null);

  const handleClick = () => {
    inputRef.current.select();
  };

  return (
    <>
      <input type="text" ref={inputRef} />
      <button onClick={handleClick}>Click To focus on input</button>
    </>
  );
}

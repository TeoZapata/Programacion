import { useEffect, useState } from "react";

export default function UseEffectComponent() {
  const [data, setData] = useState([]);
  const url = "https://dummyjson.com/users";
  const fetchDataSpeakers = async () => {
    try {
      const response = await fetch(url);
      const data = await response.json();
      setData(data.users);
    } catch (error) {
      console.log("Error => ", error);
    }
  };
  useEffect(() => {
    fetchDataSpeakers();
  }, []);

  return (
    <>
      <ul>
        {data.map((item) => (
          <li key={item.id}>
            {item.firstName === "Mateo"
              ? "Aqui esta Ingeniero Mateos"
              : item.firstName}
          </li>
        ))}
      </ul>
    </>
  );
}

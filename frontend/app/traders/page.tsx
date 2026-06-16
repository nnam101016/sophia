"use client";

import {useState} from "react";
import Sidebar from "../components/Sidebar";


export default function Traders(){


const [token,setToken]=useState("");
const [sort,setSort]=useState("entry_mc");
const [data,setData] = useState<any[]>([]);
const [loading,setLoading]=useState(false);



async function analyze(){


setLoading(true);


const res = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/traders/analyze`,
{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

token,

sort_by:sort

})

}

);



const result = await res.json();

setData(result.wallets || []);

setLoading(false);


}



return (

<div className="min-h-screen bg-black text-white">


<Sidebar/>


<main className="ml-64 p-10">


<h1 className="text-4xl font-bold">
Token Traders
</h1>



<div className="mt-6">


<input

className="
bg-gray-900
p-3
rounded-xl
w-full
"

placeholder="Token address"

onChange={
e=>setToken(e.target.value)
}

/>



<select

className="
mt-3
bg-gray-900
p-3
rounded-xl
"

onChange={
e=>setSort(e.target.value)
}

>


<option value="entry_mc">
Entry MC
</option>


<option value="pnl">
PNL
</option>


</select>



<button

onClick={analyze}

className="
ml-3
bg-white
text-black
p-3
rounded-xl
"

>

{
loading?
"Scanning..."
:
"Analyze"
}


</button>


</div>





<div className="mt-8 space-y-4">


{
Array.isArray(data) && data.map(
(w,i)=>(


<div

key={i}

className="
bg-gray-950
border
border-gray-800
rounded-xl
p-5
"

>


<p className="font-mono">
{w.address}
</p>


<p>
MC:
${(w.entry_mc/1000).toFixed(1)}K
</p>


<p>
PNL:
${w.pnl.toFixed(0)}
({w.pnl_percent.toFixed(1)}%)
</p>



<p>
Trades:
{w.buy_txs}
-
{w.sell_txs}
</p>



<p>
Volume:
${w.buy_volume.toFixed(0)}
-
${w.sell_volume.toFixed(0)}
</p>



<a

href={w.gmgn}

target="_blank"

className="text-blue-400"

>

GMGN

</a>


</div>


)

)

}


</div>


</main>

</div>

)

}
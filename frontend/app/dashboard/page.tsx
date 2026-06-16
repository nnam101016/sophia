"use client";

import { useState } from "react";
import Sidebar from "../components/Sidebar";


export default function Dashboard() {


const [token,setToken] = useState("");
const [loading,setLoading] = useState(false);
const [result,setResult] = useState<any>(null);



async function analyzeToken(){


if(!token){
    return;
}


setLoading(true);


try {


const res = await fetch(
    "http://localhost:8000/wallet/analyze",
    {
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            token: token
        })
    }
);



const data = await res.json();


setResult(data);



}

catch(err){

console.log(err);

}


setLoading(false);


}



return (

<div className="min-h-screen bg-black text-white">


<Sidebar />


<main
className="
ml-64
p-10
"
>


<h1 className="text-4xl font-bold">
Sophia Intelligence
</h1>


<p className="text-gray-400 mt-2">
Blockchain wallet analysis platform
</p>





<div
className="
mt-10
border
border-gray-800
rounded-2xl
p-6
bg-gray-950
"
>


<h2 className="text-2xl font-bold">
Token Intelligence
</h2>



<input

className="
mt-5
w-full
bg-black
border
border-gray-700
rounded-lg
p-3
"

placeholder="Enter token address"

value={token}

onChange={
e=>setToken(e.target.value)
}

/>



<button

onClick={analyzeToken}

className="
mt-4
px-6
py-3
rounded-lg
bg-white
text-black
"

>

{
loading
?
"Analyzing..."
:
"Analyze"
}


</button>



{
result && (

<div className="mt-8 space-y-6">


{/* Summary */}

<div className="
grid
md:grid-cols-3
gap-5
">


<Stat
title="Wallets Scanned"
value={result.wallets_scanned}
/>


<Stat
title="Clusters"
value={result.clusters}
/>


<Stat
title="Token"
value={result.token.slice(0,8)+"..."}
/>


</div>





{/* Cluster Cards */}

{

result.results?.map(
(cluster:any,index:number)=>(


<div

key={index}

className="
bg-gray-950
border
border-gray-800
rounded-2xl
p-6
"

>


<div className="flex justify-between">


<div>

<h2 className="text-2xl font-bold">

Cluster #{cluster.cluster}

</h2>


<p className="text-gray-400">

Size: {cluster.size}

</p>


</div>



<div className="
bg-purple-500/20
px-4
py-2
rounded-xl
"
>

{cluster.dominant_bot}

</div>



</div>





<p className="mt-3 text-gray-400">

Estimated Winrate:

<span className="text-white font-bold">

{" "}
{cluster.est_wr}%

</span>

</p>





{/* wallets */}

<h3 className="
mt-6
font-bold
">

Wallets

</h3>



<div className="space-y-3 mt-3">


{

cluster.wallets?.map(
(wallet:any,i:number)=>(


<div

key={i}

className="
bg-black
border
border-gray-800
rounded-xl
p-4
"

>


<p className="font-mono text-sm">

{wallet.address}

</p>


<div className="flex gap-5 mt-2 text-gray-400">


<span>

BOT:
{" "}
{wallet.bot}

</span>



<span>

WR:
{" "}
{wallet.wr}%

</span>


</div>



<a

href={wallet.gmgn}

target="_blank"

className="
text-blue-400
text-sm
"

>

Open GMGN

</a>



</div>


)

)

}


</div>





{/* shared tokens */}

<h3 className="
mt-6
font-bold
">

Shared Narrative Tokens

</h3>


<div className="mt-3 space-y-1">


{

cluster.shared_tokens?.slice(0,10)
.map(
(t:any)=>(


<div
key={t.address}

className="
text-gray-400
font-mono
text-sm
"

>

{t.address}

<span className="text-white">

{" "}
({t.count})

</span>


</div>


)

)

}



</div>



</div>


)

)


}



</div>

)
}


</div>









</main>


</div>

)

}






function Stat(
{
title,
value
}:{
title:string,
value:string
}
){


return (


<div

className="
bg-gray-950
border
border-gray-800
rounded-xl
p-5
"

>


<p className="text-gray-400">
{title}
</p>


<p className="text-3xl font-bold mt-2">
{value}
</p>



</div>


)

}









function ToolCard(
{
title,
desc
}:{
title:string,
desc:string
}
){


return (


<div

className="
bg-gray-950
border
border-gray-800
rounded-xl
p-6
hover:border-gray-500
transition
"

>


<h3 className="text-xl font-bold">
{title}
</h3>



<p className="text-gray-400 mt-2">
{desc}
</p>



</div>


)

}
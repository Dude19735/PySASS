/* ===================================================================== */
/* Select the binary file */
select 
   B.BinaryId as BId, 
   B.Arch as Arch, 
   B.Name as Name,
   M.MiscValue as BinaryDecoded
from Binary B
  inner join BinaryMisc M on B.BinaryId = M.BinaryId and M.TypeId = (
     select TypeId from Type T where T.Category = 'BinaryMisc' and T.Name = 'BinaryDecoded'
  )
order by M.MiscValue desc, B.Name asc

/* ===================================================================== */
/* Select all register numbers */
select
  K.KernelId as KernelId,
  M.KernelMiscId as KernelMiscId,
  K.Name as KernelName,
  T.Name as TypeName,
  M.MiscValue as MiscValue,
  M.AdditionalInfo as AdditionalInfo
from Kernel K
inner join KernelMisc M on M.KernelId = K.KernelId
inner join Type T on T.TypeId = M.TypeId

/* ===================================================================== */
/* Select all available kernels */
select 
   K.KernelId as KId,
   K.BinaryId as BinaryId,
   K.Name as Name,
   M.MiscValue as KernelDecoded
from Binary B
  inner join Kernel K on B.BinaryId = K.BinaryId
  inner join KernelMisc M on K.KernelId = M.KernelId and M.TypeId = (
     select TypeId from Type T where T.Category = 'KernelMisc' and T.Name = 'KernelDecoded'
  )
order by M.MiscValue desc, K.Name asc

/* ===================================================================== */
/* Select all instruction headers inside the kernel */
select 
   I.InstrId as InstrId,
   I.KernelId as KernelId,
   K.BinaryId as BinaryId,
   I.Code as Code,
   I.Class as InstrClass,
   I.Desc as Desc,
   I.TypeDesc as TypeDesc,
   count(U.UniverseId) as UniverseCount
from Kernel K
inner join Instr I on I.KernelId = K.KernelId
inner join Universe U on U.InstrId = I.InstrId
where K.KernelId = 1
group by I.InstrId
order by K.KernelId asc, I.InstrId asc

select * from Universe U where U.InstrId = 1

select 
  I.KernelId as KernelId,
  T.Name as TypeName,
  M.InstrMiscId as MiscId,
  M.InstrId as ParentId,
  M.MiscValue as MiscValue,
  M.AdditionalInfo as AdditionalInfo
from InstrMisc M
inner join Type T on T.TypeId = M.TypeId
inner join Instr I on I.InstrId = M.InstrId
where I.KernelId = 1
order by I.KernelId asc, M.InstrId asc, M.InstrMiscId asc

/* ===================================================================== */
/* Select universe */
select 
   1 as level,
   U.InstrId as InstrId, 
   U.UniverseId as UId,
   C.UniverseComponentId as CId,
   NULL as SId,
   C.SeqNr as SeqNr,
   T.Name as TypeName,
   C.InstrFieldAlias as Alias,
   C.BitFrom as BitFrom,
   C.BitTo as BitTo,
   C.SassBits as SassBits,
   C.ValueName as ValueName,
   C.ClassDef as ClassDef
from Instr I
inner join Universe U on U.InstrId = I.InstrId
inner join UniverseComponent C on C.UniverseId = U.UniverseId
inner join Type T on T.TypeId = C.TypeId
where I.InstrId = 25 and C.UniverseComponentId = 433 and C.SelfParentId is NULL

with RECURSIVE hierarchy as (
select
  I.InstrId as InstrId,
  C.UniverseId as UniverseId,
  C.UniverseComponentId as UniverseComponentId, 
  1 as Level,
  0 as SelfParentId,
  C.SeqNr as SeqNr,
  T.Name as TypeName,
  C.InstrFieldAlias as Alias,
  C.BitFrom as BitFrom,
  C.BitTo as BitTo,
  C.SassBits as SassBits,
  C.ValueName as ValueName,
  C.ValueType as ValueType,
  C.ClassDef as ClassDef
from UniverseComponent C
  inner join Universe U on U.UniverseId = C.UniverseId
  inner join Instr I on I.InstrId = U.InstrId
  inner join Type T on T.TypeId = C.TypeId
where I.InstrId in (4,5,6) and C.SelfParentId is NULL
union all
select 
  P.InstrId as InstrId,
  P.UniverseId as UniverseId,
  C.UniverseComponentId as UniverseComponentId, 
  P.Level+1 as Level,
  C.SelfParentId as SelfParentId,
  C.SeqNr as SeqNr,
  T.Name as TypeName,
  C.InstrFieldAlias as Alias,
  C.BitFrom as BitFrom,
  C.BitTo as BitTo,
  C.SassBits as SassBits,
  C.ValueName as ValueName,
  C.ValueType as ValueType,
  C.ClassDef as ClassDef
from UniverseComponent C
  inner join Type T on T.TypeId = C.TypeId
  inner join hierarchy P on P.UniverseComponentId = C.SelfParentId
)
select * from hierarchy
/*where TypeName = 'func'*/
order by InstrId, UniverseId, UniverseComponentId, Level, SeqNr


select * from UniverseComponent where SelfParentId = 441
select * from UniverseComponent where UniverseComponentId = 73

select 
  U.InstrId, 
  count(U.UniverseId) as UniverseCount,
  group_concat(U.UniverseId, ',') as UniverseIds
from Universe U
inner join Instr I on I.InstrId = U.InstrId
where I.KernelId = 2
group by U.InstrId
order by U.InstrId asc

/* ===================================================================== */
/* Class definition */

select 
  T.Name as TypeName,
  I.SeqNr as SeqNr,
  I.Content as Content,
  I.AdditionalInfo as AdditionalInfo
from InstrClassDef I
inner join Type T on T.TypeId = I.TypeId
where I.InstrId = 35

/* ===================================================================== */
/* Select predicate evaluation */
select
  P.PredicateName as PredicateName,
  P.SourceType as SourceType,
  P.PredicateValue = PredicateValue,
  P.SourceOperand = SourceOperand,
  P.Ref_UniverseComponentId as UniverseComponentId,
  C.ClassDef as ClassDef
from UniverseEval U
inner join UniverseEvalPredicate P on P.UniverseEvalId = U.UniverseEvalId
left outer join UniverseComponent C on C.UniverseComponentId = P.Ref_UniverseComponentId
where U.UniverseId = 11

/* ===================================================================== */
/* Select encoding evaluation */
with RECURSIVE hierarchy as (
select
  U.UniverseId as UniverseId,
  E.UniverseEvalEncodingId as UniverseEvalEncodingId,
  0 as SelfParentId,
  E.SeqNr as SeqNr,
  1 as Level,
  T.Name as TypeName,
  E.Expr as Expr,
  E.SassBitsStr as SassBitsStr,
  E.BitFrom as BitFrom,
  E.BitTo as BitTo,
  E.Ref0_UniverseComponentId as UniverseComponentId
from UniverseEvalEncoding E 
  inner join Type T on T.TypeId = E.TypeId
  inner join UniverseEval U on U.UniverseEvalId = E.UniverseEvalId
  inner join Universe UV on UV.UniverseId = U.UniverseId
  inner join Instr I on I.InstrId = UV.InstrId
where I.InstrId = 15
union all
select
  P.UniverseId as UniverseId,
  E.UniverseEvalEncodingId as UniverseEvalEncodingId,
  E.SelfParentId as SelfParentId,
  E.SeqNr as SeqNr,
  P.Level + 1 as Level,
  T.Name as TypeName,
  E.Expr as Expr,
  E.SassBitsStr as SassBitsStr,
  E.BitFrom as BitFrom,
  E.BitTo as BitTo,
  E.Ref0_UniverseComponentId as UniverseComponentId
from UniverseEvalEncoding E 
  inner join Type T on T.TypeId = E.TypeId
  inner join hierarchy P on P.UniverseEvalEncodingId = E.SelfParentId
)
select * from hierarchy
order by UniverseId, UniverseEvalEncodingId, Level

select * from UniverseEvalEncoding
select * from UniverseComponent where UniverseComponentId = 448

/* ===================================================================== */
/* Select sub encoding for things like tables */
select
  T.Name as TypeName,
  P.UniverseEvalEncodingId as UnverseEvalEncodingId,
  P.Expr as Expr,
  P.SassBitsStr as SassBitsStr,
  P.BitFrom as BitFrom,
  P.BitTo as BitTo,
  C.ClassDef as ClassDef
from UniverseEvalEncoding P
inner join Type T on T.TypeId = P.TypeId
left outer join UniverseComponent C on C.UniverseComponentId = P.Ref_UniverseComponentId
where P.SelfParentId = 212

/* ===================================================================== */
/* Select for latencies */
select 
  L.InstrLatencyId as InstrLatencyId,
  L.SeqNr as SeqNr,
  L.TypeName as TypeName,
  L.Input as Input,
  L.TableName as TableName,
  L.Row as Row,
  L.Col as Col,
  L.Cross as Cross,
  L.Val as Val
from InstrLatency L
where L.InstrId = 25
order by L.SeqNr asc

/* ===================================================================== */
/* Select all graph nodes */
select 
  G.GraphNodeId as GraphNodeId,
  I.InstrId as InstrId,
  G.SeqNr as SeqNr,
  I.Code as Code,
  I.Class as Class,
  case 
    when C.Ref0_InstrId == I.InstrId
	then 1
	else 0
  end as IsCycleStart,
  case 
    when C.Ref1_InstrId == I.InstrId
	then 1
	else 0
  end as IsCycleCondition,
  case 
    when GC.Ref1_InstrId == I.InstrId
	then 1
	else 0
  end as IsBranchCondition,
  case 
    when C.GraphCycleId is not NULL
    then C.GraphCycleId 
	else -1
  end as CycleId,
  G.ParentLabel as InstrGroup
from GraphNode G
  inner join KernelGraph K on K.KernelGraphId = G.KernelGraphId
  left outer join Instr I on I.InstrId = G.Ref0_InstrId
  left outer join GraphCycle C on C.GraphCycleId = G.Ref1_GraphCycleId
  left outer join GraphCondition GC on GC.Ref1_InstrId = I.InstrId
where K.KernelId = 1
order by G.GraphNodeId asc;

1	1	0		88	2025-05-14 12:31:21
2	1	1		138	2025-05-14 12:31:21
3	1	2		160	2025-05-14 12:31:21
4	1	3		224	2025-05-14 12:31:21


/* ===================================================================== */
/* Select all graph edges with appended conditions */
select 
  E.GraphEdgeId as GraphEdgeId,
  GF.GraphNodeId as FromGraphNodeId,
  IGF.Code as FromCode,
  GT.GraphNodeId as ToGraphNodeId,
  IGT.Code as ToCode,
  case 
    when C.Ref1_InstrId is not NULL 
	then C.Ref1_InstrId 
	else -1 end as ConditionInstrId,
  case 
    when CF.GraphCycleId is not NULL 
	 and CT.GraphCycleId is not NULL 
	 and CF.GraphCycleId = CT.GraphCycleId 
	then CT.GraphCycleId 
	else -1 
   end as GraphCycleId
from GraphEdge E
  inner join KernelGraph K on K.KernelGraphId = E.KernelGraphId
  inner join GraphNode GF on GF.GraphNodeId = E.Ref0_GraphNodeId
  inner join GraphNode GT on GT.GraphNodeId = E.Ref1_GraphNodeId
  inner join Instr IGF on IGF.InstrId = GF.Ref0_InstrId
  inner join Instr IGT on IGT.InstrId = GT.Ref0_InstrId
  left outer join GraphCycle CF on CF.GraphCycleId = GF.Ref1_GraphCycleId
  left outer join GraphCycle CT on CT.GraphCycleId = GT.Ref1_GraphCycleId
  left outer join GraphCondition C on C.Ref0_GraphEdgeId = E.GraphEdgeId
where K.Kernelid = 1;

select * from GraphNode;
select * from GraphEdge;
select * from GraphCycle;
select * from GraphCondition;








export enum ModelId {
  gpt_4o_realtime = "gpt-4o-realtime",
  llama3_1_latest = "llama3.1:latest",
}

export interface Model {
  id: ModelId;
  name: string;
}

export const models: Model[] = [
  {
    id: ModelId.gpt_4o_realtime,
    name: "gpt-4o-realtime",
  },
  {
    id: ModelId.llama3_1_latest,
    name: "llama3.1_latest",
  },
];

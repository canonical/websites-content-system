export interface IPage {
  name: string;
  title: string;
  description: string;
  link: string;
  children: IPage[];
}

export interface IPagesResponse {
  data: {
    name: string;
    templates: IPage;
  };
}

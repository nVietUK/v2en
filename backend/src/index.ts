import { ApolloServer } from "apollo-server-express";
import Express from "express";
import { buildSchema } from "type-graphql";
import "reflect-metadata";
import { DataSource } from "typeorm";
import { RegisterResolver } from "./modules/user/Register";

const main = async () => {
  const appDataSource = new DataSource({
    name: "default",
    type: "mysql",
    host: "localhost",
    port: 3306,
    username: "admin",
    password: "Vanh@Mysql2006",
    database: "typegraphql",
    synchronize: true,
    logging: true,
    entities: ["src/entity/*.*"],
  });

  appDataSource.initialize()
    .then(() => {
      console.log('Data source has been initialized!')
    })
    .catch((err) => {
      console.error('Error during initialized data source', err)
    })

  const schema = await buildSchema({
    resolvers: [RegisterResolver],
  });

  const apolloServer = new ApolloServer({ schema: schema });

  const app = Express();
  const port = 3000;

  await apolloServer.start();
  apolloServer.applyMiddleware({ app });

  app.listen(port, () => {
    console.log("GraphQL start on port " + port);
  });
};
main();

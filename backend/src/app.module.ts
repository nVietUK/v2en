import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UserModule } from './user/user.module';
import { DataModule } from './data/data.module';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { DirectiveLocation, GraphQLDirective } from 'graphql';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data/data.entity';

@Module({
	imports: [
		TypeOrmModule.forRoot({
			name: 'Data',
			type: 'mysql',
			host: 'localhost',
			port: 3306,
			username: 'admin',
			password: 'Vanh@Mysql2006',
			database: 'typegraphql',
			synchronize: true,
			logging: true,
			autoLoadEntities: true,
			entities: [Data],
		}),
		TypeOrmModule.forFeature([Data]),
		UserModule,
		DataModule,
		GraphQLModule.forRoot<ApolloDriverConfig>({
			autoSchemaFile: 'schema.gql',
			driver: ApolloDriver,
			installSubscriptionHandlers: true,
			buildSchemaOptions: {
				directives: [
					new GraphQLDirective({
						name: 'upper',
						locations: [DirectiveLocation.FIELD_DEFINITION],
					}),
				],
			},
		}),
	],
	controllers: [AppController],
	providers: [AppService],
})
export class AppModule {}

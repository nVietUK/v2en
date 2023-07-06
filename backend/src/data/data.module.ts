import { Module } from '@nestjs/common';
import { DataResolver } from './data.resolver';
import { DataService } from './data.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { DataController } from './data.controller';
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
	providers: [DataResolver, DataService],
	imports: [
		TypeOrmModule.forFeature([Data]),
		TypeOrmModule.forRootAsync({
			imports: [ConfigModule],
			useFactory: async (configService: ConfigService) => ({
				type: 'mysql',
				host: configService.get('DB_HOST'),
				port: configService.get('DB_PORT'),
				username: configService.get('DB_USERNAME'),
				password: configService.get('DB_PASSWORD'),
				database: configService.get('DB_NAME'),
				synchronize: true,
				logging: true,
				autoLoadEntities: true,
				entities: [Data],
			}),
			inject: [ConfigService],
		}),
	],
	controllers: [DataController],
})
export class DataModule {}

import { Module } from '@nestjs/common';
import { DataController } from './data.controller';
import { DataService } from './data.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { DataRepository } from './data.repository';
import { DataResolver } from './data.resolver';
import { DataSource } from 'typeorm';

const mainDataSource = new DataSource({
	connectorPackage: 'mysql2',
	type: 'mysql',
	name: 'default',
});
export const mainDataRepository = new DataRepository(mainDataSource);
export const mainDataService = new DataService(mainDataRepository);

@Module({
	controllers: [DataController],
	providers: [DataService, DataRepository, DataResolver],
	imports: [TypeOrmModule.forFeature([Data])],
})
export class DataModule {}

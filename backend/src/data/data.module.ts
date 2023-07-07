import { Module } from '@nestjs/common';
import { DataController } from './data.controller';
import { DataService } from './data.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { DataResolver } from './data.resolver';

@Module({
	controllers: [DataController],
	providers: [DataService, DataResolver],
	imports: [TypeOrmModule.forFeature([Data])],
})
export class DataModule {}
